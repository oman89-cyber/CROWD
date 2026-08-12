"""Step 12 tests: Live Video → Crowd Intelligence Pipeline."""

import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import urllib.request
import urllib.error
import json
import time

BASE = "http://127.0.0.1:8000"
PASS = 0
FAIL = 0

def post(path, body):
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        r = urllib.request.urlopen(req)
        return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

def get(path):
    try:
        r = urllib.request.urlopen(f"{BASE}{path}")
        return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        print(f"  FAIL  {name}  {detail}")

print("\n=== Test 1: Backend Intelligence API is accessible ===")
code1, body1 = get("/api/intelligence/live")
check("GET /api/intelligence/live returns 200", code1 == 200)
check("Response has 'zones'", "zones" in body1)
check("Response has 'bottlenecks'", "bottlenecks" in body1)

print("\n=== Test 2: Intelligence API accepts track observations ===")
test_tracks = [
    {"track_id": "TRACK_001", "zone_id": "CORRIDOR_C", "timestamp": 1.0},
    {"track_id": "TRACK_002", "zone_id": "CORRIDOR_C", "timestamp": 1.0},
    {"track_id": "TRACK_003", "zone_id": "GATE_C", "timestamp": 1.0},
]
code2, body2 = post("/api/intelligence/analyze", {"tracks": test_tracks})
check("POST /api/intelligence/analyze returns 200", code2 == 200)
check("Analysis response has zones", "zones" in body2)
check("Analysis response has bottlenecks", "bottlenecks" in body2)

print("\n=== Test 3: Intelligence state is updated ===")
code3, body3 = get("/api/intelligence/live")
check("Live state updated", code3 == 200)

# Find CORRIDOR_C zone
corridor_c = None
for zone in body3.get("zones", []):
    if zone["zone_id"] == "CORRIDOR_C":
        corridor_c = zone
        break

check("CORRIDOR_C zone found", corridor_c is not None)
if corridor_c:
    check("CORRIDOR_C people count updated", corridor_c["people"] == 2)
    check("CORRIDOR_C has density_ratio", "density_ratio" in corridor_c)
    check("CORRIDOR_C has risk_score", "risk_score" in corridor_c)

print("\n=== Test 4: Empty track list is rejected ===")
code4, body4 = post("/api/intelligence/analyze", {"tracks": []})
check("Empty tracks returns 400", code4 == 400)

print("\n=== Test 5: High-density scenario updates risk ===")
# Send many tracks to CORRIDOR_C
high_density_tracks = [
    {"track_id": f"TRACK_{i:03d}", "zone_id": "CORRIDOR_C", "timestamp": 2.0}
    for i in range(4500)
]
code5, body5 = post("/api/intelligence/analyze", {"tracks": high_density_tracks})
check("High-density analysis returns 200", code5 == 200)

# Check if risk is elevated
corridor_risk = None
for zone in body5.get("zones", []):
    if zone["zone_id"] == "CORRIDOR_C":
        corridor_risk = zone.get("risk_score", 0.0)
        break

check("High-density elevates risk score", corridor_risk and corridor_risk > 0.4)

print("\n=== Test 6: Zone occupancy calculations are correct ===")
code6, body6 = post("/api/intelligence/analyze", {"tracks": [
    {"track_id": "TRACK_A", "zone_id": "GATE_C", "timestamp": 3.0},
    {"track_id": "TRACK_B", "zone_id": "GATE_C", "timestamp": 3.0},
    {"track_id": "TRACK_C", "zone_id": "BLOCK_C", "timestamp": 3.0},
]})
check("Multi-zone analysis returns 200", code6 == 200)

gate_c = None
block_c = None
for zone in body6.get("zones", []):
    if zone["zone_id"] == "GATE_C":
        gate_c = zone
    elif zone["zone_id"] == "BLOCK_C":
        block_c = zone

check("GATE_C has 2 people", gate_c and gate_c["people"] == 2)
check("BLOCK_C has 1 person", block_c and block_c["people"] == 1)

print("\n=== Test 7: Regression - Existing endpoints still work ===")
code_ticket, _ = post("/api/ticket/verify", {"ticket_id": "T0004"})
check("Ticket verification works", code_ticket == 200)

code_route, _ = post("/api/route", {"session_id": "CS-1021", "destination": "SEAT_C124"})
check("Static routing works", code_route == 200)

code_crowd_route, _ = post("/api/route/crowd-aware", {"session_id": "CS-1021", "destination": "SEAT_C124"})
check("Crowd-aware routing works", code_crowd_route == 200)

code_sim, _ = post("/api/simulation", {"crowd_size": 40000, "event_phase": "HALFTIME"})
check("Simulation works", code_sim == 200)

code_health, _ = get("/health")
check("Health check works", code_health == 200)

print(f"\n{'=' * 60}")
print(f"STEP 12 TESTS — PASSED: {PASS}   FAILED: {FAIL}")
if FAIL > 0:
    sys.exit(1)
print("All Step 12 tests passed!")
