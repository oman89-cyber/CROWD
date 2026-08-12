"""Step 10 tests: Dynamic Crowd-Aware Routing."""

import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import urllib.request
import urllib.error
import json

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

# We will start the server and tests might be stateful.
# If previous tests left some state, we can reset it by sending a 0 crowd size tracks, but 0 tracks gets rejected (empty tracks -> 400).
# Let's send 1 track in an unused zone to simulate a near-empty venue for fallback.
print("\n=== Test 1: Missing / Low-occupancy crowd state acts as static fallback ===")
tracks_empty = [{"track_id": "NONE", "zone_id": "GATE_A", "timestamp": 10.0}]
post("/api/intelligence/analyze", {"tracks": tracks_empty})

code1, body1 = post("/api/route/crowd-aware", {"session_id": "CS-1021", "destination": "WASHROOM_A"})
check("HTTP 200", code1 == 200)
check("route_mode is static_fallback or crowd_aware (with no reroute)", body1.get("route_mode") in ("static_fallback", "crowd_aware"))
check("original_route matches recommended_route", body1.get("original_route") == body1.get("recommended_route"))
check("rerouted is False", body1.get("rerouted") is False)
static_path = body1.get("original_route")
check("Static path starts at P3", static_path[0] == "P3" if static_path else False)


print("\n=== Test 2: Low-risk crowd state keeps original route ===")
tracks_low = [{"track_id": f"LOW_{i}", "zone_id": "CORRIDOR_C", "timestamp": 10.0} for i in range(10)]
post("/api/intelligence/analyze", {"tracks": tracks_low})
code_low, body_low = post("/api/route/crowd-aware", {"session_id": "CS-1021", "destination": "WASHROOM_A"})
check("HTTP 200", code_low == 200)
check("route_mode is crowd_aware", body_low.get("route_mode") == "crowd_aware")
check("rerouted is False", body_low.get("rerouted") is False)
check("recommended_route is static path", body_low.get("recommended_route") == static_path)


print("\n=== Test 3: Moderate-risk scenario prevents unstable rerouting ===")
# SECURITY_C capacity is 300. 150 people -> density=0.5, risk=0.5*0.5=0.25
# Affected distance = 60. Penalty = 60. Original cost=360->420. Alternative=410.
# Improvement = 10 / 420 = 2.3% < 10% threshold.
tracks_mod = [{"track_id": f"MOD_{i}", "zone_id": "SECURITY_C", "timestamp": 10.0} for i in range(150)]
post("/api/intelligence/analyze", {"tracks": tracks_mod})
code_mod, body_mod = post("/api/route/crowd-aware", {"session_id": "CS-1021", "destination": "WASHROOM_A"})
check("HTTP 200", code_mod == 200)
check("rerouted is False", body_mod.get("rerouted") is False)


print("\n=== Test 4: High-risk bottleneck is penalized and route is changed ===")
# CORRIDOR_C capacity is 5000. 4500 people -> density=0.9, risk is high
tracks_crit = [{"track_id": f"CRIT_{i}", "zone_id": "CORRIDOR_C", "timestamp": 10.0} for i in range(4500)]
post("/api/intelligence/analyze", {"tracks": tracks_crit})
code_crit, body_crit = post("/api/route/crowd-aware", {"session_id": "CS-1021", "destination": "WASHROOM_A"})
check("HTTP 200", code_crit == 200)
check("rerouted is True", body_crit.get("rerouted") is True)
check("original_route != recommended_route", body_crit.get("original_route") != body_crit.get("recommended_route"))
check("Reason is provided", "Original route contains a high-risk bottleneck" in body_crit.get("reason", "") or "Alternative route" in body_crit.get("reason", ""))
check("CORRIDOR_C is not in recommended_route", "CORRIDOR_C" not in body_crit.get("recommended_route"))


print("\n=== Test 5: Invalid session returns 404 ===")
code_inv_sess, body_inv_sess = post("/api/route/crowd-aware", {"session_id": "NOSESSION", "destination": "WASHROOM_A"})
check("HTTP 404", code_inv_sess == 404)


print("\n=== Test 6: Invalid destination returns 404 ===")
code_inv_dest, body_inv_dest = post("/api/route/crowd-aware", {"session_id": "CS-1021", "destination": "NOWHERE"})
check("HTTP 404", code_inv_dest == 404)


print("\n=== Test 7: Regression tests ===")
code_static_route, _ = post("/api/route", {"session_id": "CS-1021", "destination": "SEAT_C124"})
check("Existing static route works", code_static_route == 200)
code_ticket, _ = post("/api/ticket/verify", {"ticket_id": "T0004"})
check("Existing ticket endpoint works", code_ticket == 200)
code_sim, _ = post("/api/simulation", {"crowd_size": 40000, "event_phase": "HALFTIME"})
check("Existing simulation endpoint works", code_sim == 200)
code_intel, _ = get("/api/intelligence/live")
check("Existing intelligence endpoint works", code_intel == 200)


print(f"\n{'=' * 60}")
print(f"STEP 10 TESTS — PASSED: {PASS}   FAILED: {FAIL}")
if FAIL > 0:
    sys.exit(1)
print("All Step 10 tests passed!")
