"""Smoke tests for Step 5: venue graph + route engine."""
import urllib.request
import urllib.error
import json
import sys

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


def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        print(f"  FAIL  {name}  {detail}")


# ------------------------------------------------------------------ Test 1
print("\n=== Test 1: POST /api/route  CS-1021 -> SEAT_C124 ===")
code, body = post("/api/route", {"session_id": "CS-1021", "destination": "SEAT_C124"})
print(f"  Status: {code}")
print(f"  Body:   {json.dumps(body, indent=2)}")
check("HTTP 200", code == 200)
check("route starts at P3", body.get("route", [None])[0] == "P3")
check("route ends at SEAT_C124", body.get("route", [None])[-1] == "SEAT_C124")
check("route contains GATE_C", "GATE_C" in body.get("route", []))
check("route contains SECURITY_C", "SECURITY_C" in body.get("route", []))
check("route contains CORRIDOR_C", "CORRIDOR_C" in body.get("route", []))
check("route contains BLOCK_C", "BLOCK_C" in body.get("route", []))
check("distance is returned", isinstance(body.get("distance"), (int, float)) and body["distance"] > 0)
check("estimated_minutes is returned", isinstance(body.get("estimated_minutes"), (int, float)) and body["estimated_minutes"] > 0)
check("risk is 0.0", body.get("risk") == 0.0)

# ------------------------------------------------------------------ Test 2
print("\n=== Test 2: Invalid session_id ===")
code2, body2 = post("/api/route", {"session_id": "NOSESSION", "destination": "SEAT_C124"})
print(f"  Status: {code2}")
print(f"  Body:   {json.dumps(body2)}")
check("HTTP 404", code2 == 404)
check("message present", "message" in body2)

# ------------------------------------------------------------------ Test 3
print("\n=== Test 3: Invalid destination ===")
code3, body3 = post("/api/route", {"session_id": "CS-1021", "destination": "NONEXISTENT"})
print(f"  Status: {code3}")
print(f"  Body:   {json.dumps(body3)}")
check("HTTP 404", code3 == 404)
check("message present", "message" in body3)

# ------------------------------------------------------------------ Test 4
print("\n=== Test 4: Existing endpoints still work ===")
import urllib.request as ur
r1 = ur.urlopen(f"{BASE}/")
check("GET / returns 200", r1.status == 200)
r2 = ur.urlopen(f"{BASE}/health")
check("GET /health returns 200", r2.status == 200)
code4, body4 = post("/api/ticket/verify", {"ticket_id": "T0004"})
check("POST /api/ticket/verify returns 200", code4 == 200)
r5 = ur.urlopen(f"{BASE}/docs")
check("GET /docs returns 200", r5.status == 200)

# ------------------------------------------------------------------ Summary
print(f"\n{'='*50}")
print(f"PASSED: {PASS}   FAILED: {FAIL}")
if FAIL > 0:
    sys.exit(1)
print("All tests passed!")
