"""Smoke tests for Step 6: crowd simulation engine."""
import urllib.request
import urllib.error
import json
import sys

BASE = "http://127.0.0.1:8000"
PASS = 0
FAIL = 0

EXPECTED_ZONES = [
    "GATE_A", "GATE_B", "GATE_C", "GATE_D",
    "CORRIDOR_A", "CORRIDOR_B", "CORRIDOR_C", "CORRIDOR_D",
    "BLOCK_A", "BLOCK_B", "BLOCK_C", "BLOCK_D",
    "FOOD_A", "FOOD_B",
    "WASHROOM_A", "WASHROOM_B", "WASHROOM_C", "WASHROOM_D",
    "EXIT_A", "EXIT_B",
]


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


# ================================================================= Test 1
print("\n=== Test 1: simulate_crowd returns valid structure (HALFTIME, 40000) ===")
code, body = post("/api/simulation", {"crowd_size": 40000, "event_phase": "HALFTIME"})
print(f"  Status: {code}")
check("HTTP 200", code == 200)
check("total_people present", "total_people" in body)
check("event_phase present", "event_phase" in body)
check("zones present", "zones" in body and isinstance(body["zones"], list))

# ================================================================= Test 2
print("\n=== Test 2: total_people matches requested crowd size ===")
check("total_people == 40000", body.get("total_people") == 40000,
      f"got {body.get('total_people')}")

# ================================================================= Test 3
print("\n=== Test 3: all expected zones exist ===")
zone_ids = [z["zone_id"] for z in body.get("zones", [])]
for zid in EXPECTED_ZONES:
    check(f"zone {zid} exists", zid in zone_ids)

# ================================================================= Test 4
print("\n=== Test 4: density is calculated correctly ===")
density_ok = True
for z in body.get("zones", []):
    expected = round(min(z["people"] / z["capacity"], 1.0), 4) if z["capacity"] > 0 else 0.0
    if z["density"] != expected:
        density_ok = False
        print(f"    density mismatch for {z['zone_id']}: got {z['density']}, expected {expected}")
check("density = people/capacity for all zones", density_ok)

# ================================================================= Test 5
print("\n=== Test 5: ENTRY produces higher gate/entry-area occupancy ===")
code5, body5 = post("/api/simulation", {"crowd_size": 40000, "event_phase": "ENTRY"})
check("ENTRY HTTP 200", code5 == 200)
zones5 = {z["zone_id"]: z for z in body5.get("zones", [])}
gate_people = sum(zones5[g]["people"] for g in ["GATE_A", "GATE_B", "GATE_C", "GATE_D"])
exit_people = sum(zones5[g]["people"] for g in ["EXIT_A", "EXIT_B"])
check("ENTRY: gates have more people than exits",
      gate_people > exit_people,
      f"gates={gate_people}, exits={exit_people}")

# ================================================================= Test 6
print("\n=== Test 6: HALFTIME produces higher food/washroom/corridor occupancy ===")
code6, body6 = post("/api/simulation", {"crowd_size": 40000, "event_phase": "HALFTIME"})
zones6 = {z["zone_id"]: z for z in body6.get("zones", [])}
food_wr_people = sum(zones6[g]["people"]
                     for g in ["FOOD_A", "FOOD_B",
                               "WASHROOM_A", "WASHROOM_B",
                               "WASHROOM_C", "WASHROOM_D"])
gate_people_ht = sum(zones6[g]["people"]
                     for g in ["GATE_A", "GATE_B", "GATE_C", "GATE_D"])
check("HALFTIME: food+washrooms > gates",
      food_wr_people > gate_people_ht,
      f"food+wr={food_wr_people}, gates={gate_people_ht}")

# ================================================================= Test 7
print("\n=== Test 7: EXIT produces higher exit occupancy ===")
code7, body7 = post("/api/simulation", {"crowd_size": 40000, "event_phase": "EXIT"})
zones7 = {z["zone_id"]: z for z in body7.get("zones", [])}
exit_people_exit = sum(zones7[g]["people"] for g in ["EXIT_A", "EXIT_B"])
gate_people_exit = sum(zones7[g]["people"] for g in ["GATE_A", "GATE_B", "GATE_C", "GATE_D"])
check("EXIT: exits have more people than gates",
      exit_people_exit > gate_people_exit,
      f"exits={exit_people_exit}, gates={gate_people_exit}")

# ================================================================= Test 8
print("\n=== Test 8: same input produces same output (deterministic) ===")
_, r1 = post("/api/simulation", {"crowd_size": 40000, "event_phase": "HALFTIME"})
_, r2 = post("/api/simulation", {"crowd_size": 40000, "event_phase": "HALFTIME"})
check("deterministic: two calls produce identical output", r1 == r2)

# ================================================================= Test 9
print("\n=== Test 9: POST /api/simulation returns HTTP 200 ===")
code9, _ = post("/api/simulation", {"crowd_size": 25000, "event_phase": "PRE_EVENT"})
check("PRE_EVENT simulation HTTP 200", code9 == 200)

# ================================================================= Test 10
print("\n=== Test 10: GET /api/crowd/live returns HTTP 200 ===")
code10, body10 = get("/api/crowd/live")
check("crowd/live HTTP 200", code10 == 200)
check("crowd/live has zones", "zones" in body10 and len(body10["zones"]) > 0)
check("crowd/live has total_people", isinstance(body10.get("total_people"), int))
check("crowd/live has event_phase", isinstance(body10.get("event_phase"), str))

# ================================================================= Test 11
print("\n=== Test 11: Existing ticket endpoint still works ===")
code11, body11 = post("/api/ticket/verify", {"ticket_id": "T0004"})
check("ticket verify HTTP 200", code11 == 200)
check("ticket valid", body11.get("valid") is True)
check("session_id = CS-1021", body11.get("session_id") == "CS-1021")

# ================================================================= Test 12
print("\n=== Test 12: Existing route endpoint still works ===")
code12, body12 = post("/api/route", {"session_id": "CS-1021", "destination": "SEAT_C124"})
check("route HTTP 200", code12 == 200)
check("route starts at P3", body12.get("route", [None])[0] == "P3")
check("route ends at SEAT_C124", body12.get("route", [None])[-1] == "SEAT_C124")
check("route distance = 230", body12.get("distance") == 230.0)

# ================================================================= Test 13
print("\n=== Test 13: Flow values exist ===")
flow_ok = True
for z in body.get("zones", []):
    if "incoming_flow" not in z or "outgoing_flow" not in z:
        flow_ok = False
        break
check("all zones have incoming_flow and outgoing_flow", flow_ok)

# ================================================================= Test 14
print("\n=== Test 14: Invalid event phase ===")
code14, body14 = post("/api/simulation", {"crowd_size": 40000, "event_phase": "INVALID"})
check("invalid phase returns 400", code14 == 400)

# ================================================================= Summary
print(f"\n{'='*50}")
print(f"PASSED: {PASS}   FAILED: {FAIL}")
if FAIL > 0:
    sys.exit(1)
print("All tests passed!")
