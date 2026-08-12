"""Step 10 Detailed Analysis — Capture exact routing metrics."""

import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import urllib.request
import urllib.error
import json

BASE = "http://127.0.0.1:8000"

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

print("=" * 70)
print("STEP 10 — DETAILED ROUTING ANALYSIS")
print("=" * 70)

# Configuration values
print("\n=== Configuration ===")
print("RISK_WEIGHT = 4.0")
print("MIN_ROUTE_IMPROVEMENT = 0.10 (10%)")
print("WALKING_SPEED = 1.2 m/s")

# Test 1: Static shortest route (CS-1021 → SEAT_C124)
print("\n" + "=" * 70)
print("TEST 1: Static Shortest Route")
print("=" * 70)
code1, body1 = post("/api/route", {"session_id": "CS-1021", "destination": "SEAT_C124"})
print(f"Endpoint: POST /api/route")
print(f"Request: session_id=CS-1021, destination=SEAT_C124")
print(f"Status: {code1}")
print(f"\nOriginal Route:")
print(f"  Path: {' → '.join(body1['route'])}")
print(f"  Distance: {body1['distance']} meters")
print(f"  Time: {body1['estimated_minutes']} minutes")
print(f"  Risk: {body1['risk']}")
static_route = body1['route']
static_distance = body1['distance']

# Test 2: Low-risk crowd state (no rerouting)
print("\n" + "=" * 70)
print("TEST 2: Low-Risk Crowd State (No Rerouting)")
print("=" * 70)
tracks_low = [{"track_id": f"LOW_{i}", "zone_id": "CORRIDOR_C", "timestamp": 10.0} for i in range(50)]
post("/api/intelligence/analyze", {"tracks": tracks_low})
_, intel_low = get("/api/intelligence/live")
corridor_c_low = next(z for z in intel_low['zones'] if z['zone_id'] == 'CORRIDOR_C')
print(f"CORRIDOR_C State:")
print(f"  People: {corridor_c_low['people']}")
print(f"  Capacity: {corridor_c_low['capacity']}")
print(f"  Density: {corridor_c_low['density_ratio']:.4f} ({corridor_c_low['density_percent']:.2f}%)")
print(f"  Risk Score: {corridor_c_low['risk_score']:.4f}")
print(f"  Risk Level: {corridor_c_low['risk_level']}")
print(f"  Is Bottleneck: {corridor_c_low['is_bottleneck']}")

code2, body2 = post("/api/route/crowd-aware", {"session_id": "CS-1021", "destination": "SEAT_C124"})
print(f"\nCrowd-Aware Route:")
print(f"  Original Path: {' → '.join(body2['original_route'])}")
print(f"  Recommended Path: {' → '.join(body2['recommended_route'])}")
print(f"  Distance: {body2['distance']} meters")
print(f"  Time: {body2['estimated_minutes']} minutes")
print(f"  Risk Score: {body2['risk_score']:.4f}")
print(f"  Route Mode: {body2['route_mode']}")
print(f"  Rerouted: {body2['rerouted']}")
print(f"  Reason: {body2['reason']}")

# Test 3: High-risk CORRIDOR_C (should trigger rerouting)
print("\n" + "=" * 70)
print("TEST 3: High-Risk CORRIDOR_C (Rerouting Expected)")
print("=" * 70)
tracks_high = [{"track_id": f"HIGH_{i}", "zone_id": "CORRIDOR_C", "timestamp": 10.0} for i in range(4500)]
post("/api/intelligence/analyze", {"tracks": tracks_high})
_, intel_high = get("/api/intelligence/live")
corridor_c_high = next(z for z in intel_high['zones'] if z['zone_id'] == 'CORRIDOR_C')
print(f"CORRIDOR_C State:")
print(f"  People: {corridor_c_high['people']}")
print(f"  Capacity: {corridor_c_high['capacity']}")
print(f"  Density: {corridor_c_high['density_ratio']:.4f} ({corridor_c_high['density_percent']:.2f}%)")
print(f"  Risk Score: {corridor_c_high['risk_score']:.4f}")
print(f"  Risk Level: {corridor_c_high['risk_level']}")
print(f"  Is Bottleneck: {corridor_c_high['is_bottleneck']}")

code3, body3 = post("/api/route/crowd-aware", {"session_id": "CS-1021", "destination": "SEAT_C124"})
print(f"\nCrowd-Aware Route:")
print(f"  Original Path: {' → '.join(body3['original_route'])}")
print(f"  Recommended Path: {' → '.join(body3['recommended_route'])}")
print(f"  Distance: {body3['distance']} meters")
print(f"  Time: {body3['estimated_minutes']} minutes")
print(f"  Risk Score: {body3['risk_score']:.4f}")
print(f"  Route Mode: {body3['route_mode']}")
print(f"  Rerouted: {body3['rerouted']}")
print(f"  Reason: {body3['reason']}")

# Calculate dynamic costs
print(f"\nDynamic Cost Calculation:")
print(f"  Formula: distance × (1 + RISK_WEIGHT × risk)")
print(f"  Formula: distance × (1 + 4.0 × {corridor_c_high['risk_score']:.4f})")
print(f"  Formula: distance × {1 + 4.0 * corridor_c_high['risk_score']:.4f}")

original_has_corridor_c = 'CORRIDOR_C' in body3['original_route']
recommended_has_corridor_c = 'CORRIDOR_C' in body3['recommended_route']
print(f"\n  Original route uses CORRIDOR_C: {original_has_corridor_c}")
print(f"  Recommended route uses CORRIDOR_C: {recommended_has_corridor_c}")

# Test 4: Alternative destination to show different route
print("\n" + "=" * 70)
print("TEST 4: Alternative Destination (WASHROOM_A)")
print("=" * 70)
# Keep high-risk CORRIDOR_C from previous test
code4, body4 = post("/api/route/crowd-aware", {"session_id": "CS-1021", "destination": "WASHROOM_A"})
print(f"Request: session_id=CS-1021, destination=WASHROOM_A")
print(f"Status: {code4}")
print(f"\nCrowd-Aware Route:")
print(f"  Original Path: {' → '.join(body4['original_route'])}")
print(f"  Recommended Path: {' → '.join(body4['recommended_route'])}")
print(f"  Distance: {body4['distance']} meters")
print(f"  Time: {body4['estimated_minutes']} minutes")
print(f"  Risk Score: {body4['risk_score']:.4f}")
print(f"  Route Mode: {body4['route_mode']}")
print(f"  Rerouted: {body4['rerouted']}")
print(f"  Reason: {body4['reason']}")

# Test 5: No crowd data fallback
print("\n" + "=" * 70)
print("TEST 5: No Crowd Data Fallback")
print("=" * 70)
# Reset to minimal crowd state
tracks_reset = [{"track_id": "RESET_1", "zone_id": "GATE_A", "timestamp": 10.0}]
post("/api/intelligence/analyze", {"tracks": tracks_reset})
code5, body5 = post("/api/route/crowd-aware", {"session_id": "CS-1021", "destination": "FOOD_B"})
print(f"Request: session_id=CS-1021, destination=FOOD_B")
print(f"Status: {code5}")
print(f"\nCrowd-Aware Route:")
print(f"  Original Path: {' → '.join(body5['original_route'])}")
print(f"  Recommended Path: {' → '.join(body5['recommended_route'])}")
print(f"  Distance: {body5['distance']} meters")
print(f"  Time: {body5['estimated_minutes']} minutes")
print(f"  Risk Score: {body5['risk_score']:.4f}")
print(f"  Route Mode: {body5['route_mode']}")
print(f"  Rerouted: {body5['rerouted']}")
print(f"  Reason: {body5['reason']}")

print("\n" + "=" * 70)
print("DETAILED ANALYSIS COMPLETE")
print("=" * 70)
