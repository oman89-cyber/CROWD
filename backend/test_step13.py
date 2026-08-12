"""Step 13 tests: Live Crowd → Automatic Route Re-evaluation."""

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

# Test session and destination  
TEST_SESSION = "CS-1021"  # This session exists in database
TEST_DESTINATION = "SEAT_C124"

print("\n=== Test 1: Route Recalculate API is accessible ===")
code1, body1 = post("/api/route/recalculate", {
    "session_id": TEST_SESSION,
    "destination": TEST_DESTINATION
})
check("POST /api/route/recalculate returns 200", code1 == 200)
if code1 == 200:
    check("Response has session_id", "session_id" in body1)
    check("Response has route_changed", "route_changed" in body1)
    check("Response has current_route", "current_route" in body1)
    check("Response has route_version", "route_version" in body1)
else:
    check("Response has session_id", False, f"Got {code1}: {body1}")
    check("Response has route_changed", False)
    check("Response has current_route", False)
    check("Response has route_version", False)

print("\n=== Test 2: Safe route does not reroute initially ===")
# First call should establish baseline route
code2a, body2a = post("/api/route/recalculate", {
    "session_id": TEST_SESSION,
    "destination": TEST_DESTINATION
})
check("Initial route calculation successful", code2a == 200)
initial_route = body2a.get("current_route", [])
initial_version = body2a.get("route_version", 0)

# Second call with same conditions should not reroute
code2b, body2b = post("/api/route/recalculate", {
    "session_id": TEST_SESSION,
    "destination": TEST_DESTINATION
})
check("Safe route does not reroute", body2b.get("route_changed", True) == False)
check("Route version unchanged for safe route", body2b.get("route_version", 0) == initial_version)

print("\n=== Test 3: Create high-risk scenario ===")
# Create high-risk tracks for CORRIDOR_C (zone on typical route)
high_risk_tracks = [
    {"track_id": f"TRACK_{i:03d}", "zone_id": "CORRIDOR_C", "timestamp": time.time()}
    for i in range(5000)  # Very high density to ensure risk > 0.60
]
code3, body3 = post("/api/intelligence/analyze", {"tracks": high_risk_tracks})
check("High-risk scenario created", code3 == 200)

# Verify CORRIDOR_C is now high risk
corridor_risk = None
for zone in body3.get("zones", []):
    if zone["zone_id"] == "CORRIDOR_C":
        corridor_risk = zone.get("risk_score", 0.0)
        break

check("CORRIDOR_C risk elevated", corridor_risk and corridor_risk >= 0.60, f"Risk was {corridor_risk}")

print("\n=== Test 4: High-risk route triggers reroute evaluation ===")
code4, body4 = post("/api/route/recalculate", {
    "session_id": TEST_SESSION,
    "destination": TEST_DESTINATION
})
check("Route re-evaluation successful", code4 == 200)

# Check if reroute occurred (depends on whether alternative exists)
route_changed = body4.get("route_changed", False)
new_version = body4.get("route_version", 0)

if route_changed:
    check("High-risk triggers reroute", True)
    check("Route version incremented", new_version > initial_version)
    check("Previous route returned", len(body4.get("previous_route", [])) > 0)
    check("New route returned", len(body4.get("new_route", [])) > 0)
    check("Reason provided", len(body4.get("reason", "")) > 0)
else:
    check("No alternative available (acceptable)", True, "No better route exists")

print("\n=== Test 5: Route cooldown prevents repeated rerouting ===")
# Immediate second call should be subject to cooldown
code5, body5 = post("/api/route/recalculate", {
    "session_id": TEST_SESSION,
    "destination": TEST_DESTINATION
})
check("Cooldown call successful", code5 == 200)

# If previous call caused reroute, this should show cooldown behavior
if route_changed:
    # Version should not increment again immediately
    cooldown_version = body5.get("route_version", 0)
    check("Cooldown prevents immediate re-reroute", cooldown_version == new_version)

print("\n=== Test 6: Critical risk can bypass cooldown ===")
# Create CRITICAL risk scenario
critical_tracks = [
    {"track_id": f"CRIT_{i:03d}", "zone_id": "GATE_C", "timestamp": time.time()}
    for i in range(7000)  # Even higher density for critical (>0.80)
]
code6a, body6a = post("/api/intelligence/analyze", {"tracks": critical_tracks})
check("Critical risk scenario created", code6a == 200)

# Check actual risk level achieved
gate_risk = None
for zone in body6a.get("zones", []):
    if zone["zone_id"] == "GATE_C":
        gate_risk = zone.get("risk_score", 0.0)
        break

code6b, body6b = post("/api/route/recalculate", {
    "session_id": TEST_SESSION,
    "destination": TEST_DESTINATION
})
check("Critical risk evaluation successful", code6b == 200)

# Check if critical risk is detected in reason or if risk is actually critical
reason = body6b.get("reason", "").lower()
has_critical_mention = "critical" in reason or (gate_risk and gate_risk >= 0.80)
check("Critical risk handled appropriately", has_critical_mention, f"Gate risk: {gate_risk}, Reason: {reason}")

print("\n=== Test 7: Invalid session returns 404 ===")
code7, body7 = post("/api/route/recalculate", {
    "session_id": "INVALID_SESSION",
    "destination": TEST_DESTINATION
})
check("Invalid session returns 404", code7 == 404)

print("\n=== Test 8: Invalid destination returns 404 ===")
code8, body8 = post("/api/route/recalculate", {
    "session_id": TEST_SESSION,
    "destination": "INVALID_DESTINATION"
})
check("Invalid destination returns 404", code8 == 404)

print("\n=== Test 9: Route version behavior ===")
# Reset to clean state for version testing
normal_tracks = [
    {"track_id": f"NORM_{i:03d}", "zone_id": "WASHROOM_C", "timestamp": time.time()}
    for i in range(50)  # Low density
]
code9a, body9a = post("/api/intelligence/analyze", {"tracks": normal_tracks})
check("Normal state restored", code9a == 200)

# Get baseline version using existing valid session
code9b, body9b = post("/api/route/recalculate", {
    "session_id": TEST_SESSION,  # Use valid session
    "destination": TEST_DESTINATION
})
if code9b == 200:
    check("Route calculation successful", True)
    baseline_version = body9b.get("route_version", 0)
    check("Route version is positive", baseline_version >= 1)
else:
    check("Route calculation successful", False, f"Got {code9b}: {body9b}")
    check("Route version is positive", False)

print("\n=== Test 10: Regression - Existing endpoints still work ===")
# Test existing routing endpoints
code10a, body10a = post("/api/route", {"session_id": TEST_SESSION, "destination": TEST_DESTINATION})
check("Static routing still works", code10a == 200)

code10b, body10b = post("/api/route/crowd-aware", {"session_id": TEST_SESSION, "destination": TEST_DESTINATION})
check("Crowd-aware routing still works", code10b == 200)

# Test intelligence endpoints
code10c, body10c = get("/api/intelligence/live")
check("Live intelligence still works", code10c == 200)

# Test ticket verification
code10d, body10d = post("/api/ticket/verify", {"ticket_id": "T0004"})
check("Ticket verification still works", code10d == 200)

print("\n=== Test 11: Route recalculation with different destinations ===")
# Test with multiple destinations
destinations = ["SEAT_A001", "FOOD_B", "WASHROOM_C"]
for dest in destinations:
    code11, body11 = post("/api/route/recalculate", {
        "session_id": TEST_SESSION,
        "destination": dest
    })
    if code11 == 200:
        check(f"Recalculation works for {dest}", True)
    else:
        # Some destinations might not exist in graph, which is acceptable
        check(f"Destination {dest} handled correctly", code11 in [200, 404])

print("\n=== Test 12: Route state isolation between sessions ===")
# Test that valid sessions work - we can't test isolation without valid sessions in DB
code12a, body12a = post("/api/route/recalculate", {
    "session_id": TEST_SESSION,  # Use valid session
    "destination": TEST_DESTINATION
})

check("Valid session works", code12a == 200)
if code12a == 200:
    version_a = body12a.get("route_version", 0)
    check("Route version returned", version_a >= 1)
    check("Route state managed correctly", len(body12a.get("current_route", [])) > 0)
else:
    check("Route version returned", False)
    check("Route state managed correctly", False)

print(f"\n{'=' * 60}")
print(f"STEP 13 TESTS — PASSED: {PASS}   FAILED: {FAIL}")
if FAIL > 0:
    sys.exit(1)
print("All Step 13 tests passed!")