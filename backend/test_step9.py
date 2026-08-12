"""Step 9 tests: Crowd Intelligence Engine.

22 tests covering:
  1-2   Unique track counting & zone occupancy
  3-4   Density ratio & percent
  5-9   Density classification (LOW, MODERATE, HIGH, CRITICAL, OVERCAPACITY)
  10-11 Flow & net flow
  12-13 Risk score & classification
  14-15 Bottleneck detection & reason
  16-17 API POST success & invalid input
  18    API GET live endpoint
  19    Simulation API regression
  20    Route API regression
  21    Ticket API regression
  22    All previous tests' endpoints still work
"""

import sys
import os

# Ensure clean output on Windows consoles
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

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


# ===================================================================
# SCENARIO E: Same track across 10 frames → counted as 1 person
# ===================================================================
print("\n=== Test 1: Unique track counting (same track × 10 frames) ===")
tracks_scenario_e = [
    {"track_id": "TRACK_E01", "zone_id": "CORRIDOR_C", "timestamp": float(i)}
    for i in range(10)
]
code1, body1 = post("/api/intelligence/analyze", {"tracks": tracks_scenario_e})
check("HTTP 200", code1 == 200)
zone_c = None
for z in body1.get("zones", []):
    if z["zone_id"] == "CORRIDOR_C":
        zone_c = z
        break
check("CORRIDOR_C found", zone_c is not None)
check("people == 1 (not 10)", zone_c is not None and zone_c.get("people") == 1,
      f"got {zone_c.get('people') if zone_c else 'N/A'}")


# ===================================================================
# Test 2: Zone occupancy — multiple unique tracks
# ===================================================================
print("\n=== Test 2: Zone occupancy (3 unique tracks in CORRIDOR_C) ===")
tracks_occ = [
    {"track_id": "TRACK_001", "zone_id": "CORRIDOR_C", "timestamp": 10.0},
    {"track_id": "TRACK_002", "zone_id": "CORRIDOR_C", "timestamp": 10.0},
    {"track_id": "TRACK_003", "zone_id": "CORRIDOR_C", "timestamp": 10.0},
]
code2, body2 = post("/api/intelligence/analyze", {"tracks": tracks_occ})
zone_c2 = next((z for z in body2.get("zones", []) if z["zone_id"] == "CORRIDOR_C"), None)
check("3 unique tracks → people == 3",
      zone_c2 is not None and zone_c2.get("people") == 3,
      f"got {zone_c2.get('people') if zone_c2 else 'N/A'}")


# ===================================================================
# Test 3: Density ratio
# ===================================================================
print("\n=== Test 3: Density ratio (CORRIDOR_C capacity=5000) ===")
check("density_ratio = 3/5000 = 0.0006",
      zone_c2 is not None and zone_c2.get("density_ratio") == round(3 / 5000, 4),
      f"got {zone_c2.get('density_ratio') if zone_c2 else 'N/A'}")


# ===================================================================
# Test 4: Density percent
# ===================================================================
print("\n=== Test 4: Density percent ===")
expected_pct = round(round(3 / 5000, 4) * 100, 2)
check("density_percent matches",
      zone_c2 is not None and zone_c2.get("density_percent") == expected_pct,
      f"expected {expected_pct}, got {zone_c2.get('density_percent') if zone_c2 else 'N/A'}")


# ===================================================================
# Tests 5–9: Density classification via direct service import
# We create tracks to produce specific density ratios
# ===================================================================

# SCENARIO A: Low-density venue (< 50% → LOW)
print("\n=== Test 5: LOW density classification ===")
# CORRIDOR_C capacity = 5000, so 1000 people → 20% → LOW
tracks_low = [
    {"track_id": f"LOW_{i:04d}", "zone_id": "CORRIDOR_C", "timestamp": 10.0}
    for i in range(1000)
]
code5, body5 = post("/api/intelligence/analyze", {"tracks": tracks_low})
zone_low = next((z for z in body5.get("zones", []) if z["zone_id"] == "CORRIDOR_C"), None)
check("1000/5000 = 0.20 → LOW",
      zone_low is not None and zone_low.get("density_level") == "LOW",
      f"got level={zone_low.get('density_level') if zone_low else 'N/A'}, "
      f"ratio={zone_low.get('density_ratio') if zone_low else 'N/A'}")


# Test 6: MODERATE (0.50–<0.70)
print("\n=== Test 6: MODERATE density classification ===")
# 3000/5000 = 0.60 → MODERATE
tracks_mod = [
    {"track_id": f"MOD_{i:04d}", "zone_id": "CORRIDOR_C", "timestamp": 10.0}
    for i in range(3000)
]
code6, body6 = post("/api/intelligence/analyze", {"tracks": tracks_mod})
zone_mod = next((z for z in body6.get("zones", []) if z["zone_id"] == "CORRIDOR_C"), None)
check("3000/5000 = 0.60 → MODERATE",
      zone_mod is not None and zone_mod.get("density_level") == "MODERATE",
      f"got level={zone_mod.get('density_level') if zone_mod else 'N/A'}")


# Test 7: HIGH (0.70–<0.85)
print("\n=== Test 7: HIGH density classification ===")
# 4000/5000 = 0.80 → HIGH
tracks_high = [
    {"track_id": f"HIGH_{i:04d}", "zone_id": "CORRIDOR_C", "timestamp": 10.0}
    for i in range(4000)
]
code7, body7 = post("/api/intelligence/analyze", {"tracks": tracks_high})
zone_high = next((z for z in body7.get("zones", []) if z["zone_id"] == "CORRIDOR_C"), None)
check("4000/5000 = 0.80 → HIGH",
      zone_high is not None and zone_high.get("density_level") == "HIGH",
      f"got level={zone_high.get('density_level') if zone_high else 'N/A'}")


# Test 8: CRITICAL (0.85–1.00)
print("\n=== Test 8: CRITICAL density classification ===")
# 4500/5000 = 0.90 → CRITICAL
tracks_crit = [
    {"track_id": f"CRIT_{i:04d}", "zone_id": "CORRIDOR_C", "timestamp": 10.0}
    for i in range(4500)
]
code8, body8 = post("/api/intelligence/analyze", {"tracks": tracks_crit})
zone_crit = next((z for z in body8.get("zones", []) if z["zone_id"] == "CORRIDOR_C"), None)
check("4500/5000 = 0.90 → CRITICAL",
      zone_crit is not None and zone_crit.get("density_level") == "CRITICAL",
      f"got level={zone_crit.get('density_level') if zone_crit else 'N/A'}")


# Test 9: OVERCAPACITY (> 1.0) — SCENARIO D
print("\n=== Test 9: OVERCAPACITY density classification ===")
# 6000/5000 = 1.20 → OVERCAPACITY
tracks_over = [
    {"track_id": f"OVER_{i:04d}", "zone_id": "CORRIDOR_C", "timestamp": 10.0}
    for i in range(6000)
]
code9, body9 = post("/api/intelligence/analyze", {"tracks": tracks_over})
zone_over = next((z for z in body9.get("zones", []) if z["zone_id"] == "CORRIDOR_C"), None)
check("6000/5000 = 1.20 → OVERCAPACITY",
      zone_over is not None and zone_over.get("density_level") == "OVERCAPACITY",
      f"got level={zone_over.get('density_level') if zone_over else 'N/A'}")
check("density_ratio > 1.0 (not clamped)",
      zone_over is not None and zone_over.get("density_ratio", 0) > 1.0,
      f"got ratio={zone_over.get('density_ratio') if zone_over else 'N/A'}")


# ===================================================================
# SCENARIO F: Flow calculation — track moves GATE_C → CORRIDOR_C
# ===================================================================
print("\n=== Test 10: Flow calculation (GATE_C → CORRIDOR_C) ===")
tracks_flow = [
    # Track starts at GATE_C
    {"track_id": "FLOW_001", "zone_id": "GATE_C", "timestamp": 1.0},
    # Track moves to CORRIDOR_C
    {"track_id": "FLOW_001", "zone_id": "CORRIDOR_C", "timestamp": 5.0},
    # Another track stays at GATE_C
    {"track_id": "FLOW_002", "zone_id": "GATE_C", "timestamp": 1.0},
    {"track_id": "FLOW_002", "zone_id": "GATE_C", "timestamp": 5.0},
]
code10, body10 = post("/api/intelligence/analyze", {"tracks": tracks_flow})
gate_c = next((z for z in body10.get("zones", []) if z["zone_id"] == "GATE_C"), None)
corr_c = next((z for z in body10.get("zones", []) if z["zone_id"] == "CORRIDOR_C"), None)

check("GATE_C outgoing_flow >= 1",
      gate_c is not None and gate_c.get("outgoing_flow", 0) >= 1,
      f"got {gate_c.get('outgoing_flow') if gate_c else 'N/A'}")
check("CORRIDOR_C incoming_flow >= 1",
      corr_c is not None and corr_c.get("incoming_flow", 0) >= 1,
      f"got {corr_c.get('incoming_flow') if corr_c else 'N/A'}")


# ===================================================================
# Test 11: Net flow
# ===================================================================
print("\n=== Test 11: Net flow (CORRIDOR_C) ===")
check("net_flow = incoming - outgoing",
      corr_c is not None and corr_c.get("net_flow") == corr_c.get("incoming_flow", 0) - corr_c.get("outgoing_flow", 0),
      f"got net_flow={corr_c.get('net_flow') if corr_c else 'N/A'}")


# ===================================================================
# Test 12: Risk score range [0.0, 1.0]
# ===================================================================
print("\n=== Test 12: Risk score range ===")
# Use the overcapacity response which should have a high risk score
all_risk_valid = True
if body9.get("zones"):
    for z in body9["zones"]:
        rs = z.get("risk_score", -1)
        if rs < 0.0 or rs > 1.0:
            all_risk_valid = False
            print(f"    Out of range: {z['zone_id']} risk_score={rs}")
check("all risk_scores in [0.0, 1.0]", all_risk_valid)

# The overcapacity zone should have a meaningful (non-zero) risk
check("OVERCAPACITY zone has risk_score > 0",
      zone_over is not None and zone_over.get("risk_score", 0) > 0,
      f"got {zone_over.get('risk_score') if zone_over else 'N/A'}")


# ===================================================================
# Test 13: Risk classification
# ===================================================================
print("\n=== Test 13: Risk classification ===")
# The overcapacity zone should be CRITICAL risk
check("OVERCAPACITY → risk_level is HIGH or CRITICAL",
      zone_over is not None and zone_over.get("risk_level") in ("HIGH", "CRITICAL"),
      f"got {zone_over.get('risk_level') if zone_over else 'N/A'}")

# Low density should be LOW risk
check("LOW density → LOW risk",
      zone_low is not None and zone_low.get("risk_level") == "LOW",
      f"got {zone_low.get('risk_level') if zone_low else 'N/A'}")


# ===================================================================
# SCENARIO B/C: Bottleneck detection — high density + incoming flow
# ===================================================================
print("\n=== Test 14: Bottleneck detection ===")
# Create a high-density corridor with incoming flow
tracks_bottleneck = []
# 4500 tracks in CORRIDOR_C (90% capacity → CRITICAL density)
for i in range(4500):
    tracks_bottleneck.append(
        {"track_id": f"BN_{i:05d}", "zone_id": "CORRIDOR_C", "timestamp": 10.0}
    )
# Additional tracks flowing IN from GATE_C
for i in range(200):
    tid = f"BN_FLOW_{i:04d}"
    tracks_bottleneck.append({"track_id": tid, "zone_id": "GATE_C", "timestamp": 5.0})
    tracks_bottleneck.append({"track_id": tid, "zone_id": "CORRIDOR_C", "timestamp": 10.0})

code14, body14 = post("/api/intelligence/analyze", {"tracks": tracks_bottleneck})
zone_bn = next((z for z in body14.get("zones", []) if z["zone_id"] == "CORRIDOR_C"), None)

check("CORRIDOR_C is_bottleneck == True",
      zone_bn is not None and zone_bn.get("is_bottleneck") is True,
      f"got {zone_bn.get('is_bottleneck') if zone_bn else 'N/A'}")

# Check bottlenecks list
bn_list = body14.get("bottlenecks", [])
corridor_bn = next((b for b in bn_list if b["zone_id"] == "CORRIDOR_C"), None)
check("CORRIDOR_C in bottlenecks list",
      corridor_bn is not None)


# ===================================================================
# Test 15: Bottleneck reason
# ===================================================================
print("\n=== Test 15: Bottleneck reason ===")
check("bottleneck has non-empty reason",
      corridor_bn is not None and len(corridor_bn.get("reason", "")) > 0,
      f"got reason='{corridor_bn.get('reason') if corridor_bn else 'N/A'}'")


# ===================================================================
# Test 16: API POST /api/intelligence/analyze success
# ===================================================================
print("\n=== Test 16: API POST success ===")
simple_tracks = [
    {"track_id": "TRACK_001", "zone_id": "CORRIDOR_C", "timestamp": 10.0},
    {"track_id": "TRACK_002", "zone_id": "CORRIDOR_C", "timestamp": 10.0},
]
code16, body16 = post("/api/intelligence/analyze", {"tracks": simple_tracks})
check("HTTP 200", code16 == 200)
check("response has 'zones'", "zones" in body16)
check("response has 'bottlenecks'", "bottlenecks" in body16)
check("zones list non-empty", len(body16.get("zones", [])) > 0)


# ===================================================================
# Test 17: API invalid input handling
# ===================================================================
print("\n=== Test 17: API invalid input ===")
code17a, body17a = post("/api/intelligence/analyze", {"tracks": []})
check("empty tracks → 400", code17a == 400,
      f"got {code17a}")

code17b, _ = post("/api/intelligence/analyze", {})
check("missing tracks field → 422", code17b == 422)


# ===================================================================
# Test 18: GET /api/intelligence/live
# ===================================================================
print("\n=== Test 18: GET /api/intelligence/live ===")
code18, body18 = get("/api/intelligence/live")
check("HTTP 200", code18 == 200)
check("response has 'zones'", "zones" in body18)
check("response has 'bottlenecks'", "bottlenecks" in body18)
check("zones is a list", isinstance(body18.get("zones"), list))


# ===================================================================
# Test 19: Existing simulation API still works
# ===================================================================
print("\n=== Test 19: POST /api/simulation regression ===")
code19, body19 = post("/api/simulation", {"crowd_size": 40000, "event_phase": "HALFTIME"})
check("simulation HTTP 200", code19 == 200)
check("simulation has zones", "zones" in body19 and len(body19["zones"]) > 0)
check("simulation total_people == 40000",
      body19.get("total_people") == 40000)


# ===================================================================
# Test 20: Existing route API still works
# ===================================================================
print("\n=== Test 20: POST /api/route regression ===")
code20, body20 = post("/api/route", {"session_id": "CS-1021", "destination": "SEAT_C124"})
check("route HTTP 200", code20 == 200)
check("route starts at P3", body20.get("route", [None])[0] == "P3")
check("route ends at SEAT_C124", body20.get("route", [None])[-1] == "SEAT_C124")


# ===================================================================
# Test 21: Existing ticket API still works
# ===================================================================
print("\n=== Test 21: POST /api/ticket/verify regression ===")
code21, body21 = post("/api/ticket/verify", {"ticket_id": "T0004"})
check("ticket verify HTTP 200", code21 == 200)
check("ticket valid", body21.get("valid") is True)
check("session_id = CS-1021", body21.get("session_id") == "CS-1021")


# ===================================================================
# Test 22: GET /api/crowd/live regression
# ===================================================================
print("\n=== Test 22: All previous endpoints regression ===")
code22a, body22a = get("/api/crowd/live")
check("GET /api/crowd/live HTTP 200", code22a == 200)
check("crowd/live has zones", "zones" in body22a and len(body22a["zones"]) > 0)

code22b, _ = get("/health")
check("GET /health HTTP 200", code22b == 200)

code22c, _ = get("/")
check("GET / HTTP 200", code22c == 200)


# ===================================================================
# Summary
# ===================================================================
print(f"\n{'=' * 60}")
print(f"STEP 9 TESTS — PASSED: {PASS}   FAILED: {FAIL}")
if FAIL > 0:
    sys.exit(1)
print("All Step 9 tests passed!")
