"""Crowd Intelligence Engine — observed/tracked crowd state analysis.

This service analyses OBSERVED crowd tracks (from person detection +
anonymous centroid tracking) and converts them into actionable
crowd intelligence:

    TRACKS → ZONE OCCUPANCY → DENSITY → FLOW → RISK → BOTTLENECK

It is deliberately separate from ``crowd_service.py`` which handles
deterministic simulation.  This module handles *real* (or realistic)
observed state.

This is a hackathon crowd-risk heuristic.  It is NOT a medically or
safety-certified risk assessment system.
"""

from __future__ import annotations

from typing import Optional

from services.crowd_service import ZONE_DEFINITIONS

# ---------------------------------------------------------------------------
# Density classification thresholds (configurable constants)
# ---------------------------------------------------------------------------
# Each threshold represents the UPPER boundary (exclusive) for the level
# below it.
#
# density_ratio < 0.50           → LOW
# 0.50 ≤ density_ratio < 0.70    → MODERATE
# 0.70 ≤ density_ratio < 0.85    → HIGH
# 0.85 ≤ density_ratio ≤ 1.00    → CRITICAL
# density_ratio > 1.00           → OVERCAPACITY

DENSITY_THRESHOLD_LOW = 0.50
DENSITY_THRESHOLD_MODERATE = 0.70
DENSITY_THRESHOLD_HIGH = 0.85
DENSITY_THRESHOLD_CRITICAL = 1.00

# ---------------------------------------------------------------------------
# Risk classification thresholds (configurable constants)
# ---------------------------------------------------------------------------
# risk_score is always in [0.0, 1.0].
#
# risk_score < 0.30           → LOW
# 0.30 ≤ risk_score < 0.60    → MODERATE
# 0.60 ≤ risk_score < 0.80    → HIGH
# 0.80 ≤ risk_score ≤ 1.00    → CRITICAL

RISK_THRESHOLD_LOW = 0.30
RISK_THRESHOLD_MODERATE = 0.60
RISK_THRESHOLD_HIGH = 0.80

# ---------------------------------------------------------------------------
# Risk formula weights (configurable constants)
# ---------------------------------------------------------------------------
# risk_score = clamp(
#     RISK_WEIGHT_DENSITY   × density_ratio   +
#     RISK_WEIGHT_FLOW      × flow_pressure   +
#     RISK_WEIGHT_CAPACITY  × capacity_pressure,
#     0.0, 1.0
# )
#
# where:
#   flow_pressure     = min(incoming_flow / (capacity × FLOW_PRESSURE_FACTOR), 1.0)
#                       — normalised incoming flow relative to zone capacity
#   capacity_pressure = max(0, (density_ratio - CAPACITY_PRESSURE_ONSET)
#                              / (1.0 - CAPACITY_PRESSURE_ONSET))
#                       — ramps from 0 at ONSET to 1.0 at 100% capacity

RISK_WEIGHT_DENSITY = 0.50
RISK_WEIGHT_FLOW = 0.30
RISK_WEIGHT_CAPACITY = 0.20

FLOW_PRESSURE_FACTOR = 0.10       # 10% of capacity as flow normaliser
CAPACITY_PRESSURE_ONSET = 0.70    # capacity pressure starts at 70%

# ---------------------------------------------------------------------------
# Observation window (seconds) — tracks older than this are ignored
# ---------------------------------------------------------------------------
DEFAULT_OBSERVATION_WINDOW = 30.0

# ---------------------------------------------------------------------------
# Zone capacity lookup (built from ZONE_DEFINITIONS in crowd_service.py)
# ---------------------------------------------------------------------------
# Re-uses the authoritative capacity data; no duplicate configuration.
ZONE_CAPACITY: dict[str, int] = {
    zone_id: capacity for zone_id, _, capacity in ZONE_DEFINITIONS
}

# ---------------------------------------------------------------------------
# In-memory intelligence state (for GET /api/intelligence/live)
# ---------------------------------------------------------------------------
_current_intelligence_state: Optional[dict] = None


# ===================================================================
# Classification helpers
# ===================================================================

def classify_density(density_ratio: float) -> str:
    """Classify density ratio into a human-readable level.

    Thresholds are defined as module-level constants so they can be
    reconfigured without touching the logic.
    """
    if density_ratio < DENSITY_THRESHOLD_LOW:
        return "LOW"
    elif density_ratio < DENSITY_THRESHOLD_MODERATE:
        return "MODERATE"
    elif density_ratio < DENSITY_THRESHOLD_HIGH:
        return "HIGH"
    elif density_ratio <= DENSITY_THRESHOLD_CRITICAL:
        return "CRITICAL"
    else:
        return "OVERCAPACITY"


def classify_risk(risk_score: float) -> str:
    """Classify a risk score (0.0–1.0) into a human-readable level."""
    if risk_score < RISK_THRESHOLD_LOW:
        return "LOW"
    elif risk_score < RISK_THRESHOLD_MODERATE:
        return "MODERATE"
    elif risk_score < RISK_THRESHOLD_HIGH:
        return "HIGH"
    else:
        return "CRITICAL"


# ===================================================================
# Risk calculation
# ===================================================================

def compute_risk_score(
    density_ratio: float,
    incoming_flow: int,
    capacity: int,
) -> float:
    """Compute a deterministic crowd-risk heuristic score in [0.0, 1.0].

    Formula (hackathon heuristic — NOT safety-certified):
    ─────────────────────────────────────────────────────
    risk_score = clamp(
        0.50 × density_ratio                      ← density pressure
      + 0.30 × flow_pressure                      ← incoming-flow pressure
      + 0.20 × capacity_pressure                  ← proximity to full capacity
    , 0.0, 1.0)

    where:
      flow_pressure     = min(incoming_flow / (capacity × 0.10), 1.0)
      capacity_pressure = max(0, (density_ratio − 0.70) / 0.30)
    """
    # --- Flow pressure: incoming flow normalised against 10% of capacity ---
    flow_denom = max(capacity * FLOW_PRESSURE_FACTOR, 1)
    flow_pressure = min(incoming_flow / flow_denom, 1.0)

    # --- Capacity pressure: ramps from 0 at 70% to 1.0 at 100% -----------
    if density_ratio > CAPACITY_PRESSURE_ONSET:
        range_width = 1.0 - CAPACITY_PRESSURE_ONSET
        capacity_pressure = min(
            (density_ratio - CAPACITY_PRESSURE_ONSET) / range_width,
            1.0,
        )
    else:
        capacity_pressure = 0.0

    raw_score = (
        RISK_WEIGHT_DENSITY * density_ratio
        + RISK_WEIGHT_FLOW * flow_pressure
        + RISK_WEIGHT_CAPACITY * capacity_pressure
    )

    # Clamp to [0.0, 1.0]
    return round(max(0.0, min(raw_score, 1.0)), 4)


# ===================================================================
# Bottleneck detection
# ===================================================================

def detect_bottleneck(
    zone_id: str,
    risk_level: str,
    density_ratio: float,
    incoming_flow: int,
    net_flow: int,
) -> dict:
    """Determine whether a zone is a bottleneck.

    A zone is considered a bottleneck when:
      risk_level == "HIGH" or risk_level == "CRITICAL"

    Returns a dict with ``zone_id``, ``is_bottleneck``, and ``reason``.
    """
    is_bottleneck = risk_level in ("HIGH", "CRITICAL")

    if not is_bottleneck:
        return {
            "zone_id": zone_id,
            "is_bottleneck": False,
            "reason": "",
        }

    # Build a human-readable reason
    reasons: list[str] = []

    density_label = classify_density(density_ratio)
    if density_label in ("HIGH", "CRITICAL", "OVERCAPACITY"):
        reasons.append(f"{density_label.lower()} density ({density_ratio:.0%})")

    if incoming_flow > 0:
        reasons.append("sustained incoming flow")

    if net_flow > 0:
        reasons.append("positive net flow (more entering than leaving)")

    if not reasons:
        reasons.append(f"{risk_level.lower()} risk level")

    reason = "; ".join(reasons).capitalize()

    return {
        "zone_id": zone_id,
        "is_bottleneck": True,
        "reason": reason,
    }


# ===================================================================
# Core analysis
# ===================================================================

def analyze_tracks(
    tracks: list[dict],
    observation_window: float = DEFAULT_OBSERVATION_WINDOW,
) -> dict:
    """Analyse observed tracks and produce crowd intelligence.

    Parameters
    ----------
    tracks : list[dict]
        Each dict must contain ``track_id``, ``zone_id``, and ``timestamp``.
    observation_window : float
        Seconds; tracks older than ``max_timestamp - observation_window``
        are excluded from occupancy (but still used for flow detection).

    Returns
    -------
    dict
        ``{"zones": [...], "bottlenecks": [...]}``
    """
    if not tracks:
        return _empty_state()

    # ------------------------------------------------------------------
    # 1. Determine the observation time window
    # ------------------------------------------------------------------
    max_ts = max(t["timestamp"] for t in tracks)
    window_start = max_ts - observation_window

    # ------------------------------------------------------------------
    # 2. Build per-track history (ordered by timestamp)
    # ------------------------------------------------------------------
    # track_history[track_id] = [(timestamp, zone_id), ...]
    track_history: dict[str, list[tuple[float, str]]] = {}
    for t in tracks:
        tid = t["track_id"]
        track_history.setdefault(tid, []).append((t["timestamp"], t["zone_id"]))

    # Sort each track's observations by timestamp
    for tid in track_history:
        track_history[tid].sort(key=lambda x: x[0])

    # ------------------------------------------------------------------
    # 3. Compute UNIQUE occupancy per zone (within the observation window)
    # ------------------------------------------------------------------
    # A track is counted AT MOST ONCE per zone, using its most recent
    # observation.
    zone_tracks: dict[str, set[str]] = {zid: set() for zid in ZONE_CAPACITY}

    for tid, history in track_history.items():
        # Find the most recent observation within the window
        latest_in_window = None
        for ts, zid in reversed(history):
            if ts >= window_start:
                latest_in_window = (ts, zid)
                break

        if latest_in_window is not None:
            _, current_zone = latest_in_window
            if current_zone in zone_tracks:
                zone_tracks[current_zone].add(tid)

    # ------------------------------------------------------------------
    # 4. Compute flow (zone transitions within the observation window)
    # ------------------------------------------------------------------
    incoming_flow: dict[str, int] = {zid: 0 for zid in ZONE_CAPACITY}
    outgoing_flow: dict[str, int] = {zid: 0 for zid in ZONE_CAPACITY}

    for tid, history in track_history.items():
        # Look at consecutive observations for zone transitions
        for i in range(1, len(history)):
            prev_ts, prev_zone = history[i - 1]
            curr_ts, curr_zone = history[i]

            # Only count transitions within the observation window
            if curr_ts < window_start:
                continue

            if prev_zone != curr_zone:
                if prev_zone in outgoing_flow:
                    outgoing_flow[prev_zone] += 1
                if curr_zone in incoming_flow:
                    incoming_flow[curr_zone] += 1

    # ------------------------------------------------------------------
    # 5. Build zone intelligence
    # ------------------------------------------------------------------
    zones: list[dict] = []
    bottlenecks: list[dict] = []

    for zone_id, _, capacity in ZONE_DEFINITIONS:
        people = len(zone_tracks[zone_id])

        # Density — NOT clamped; can exceed 1.0 for overcapacity
        density_ratio = round(people / capacity, 4) if capacity > 0 else 0.0
        density_percent = round(density_ratio * 100, 2)
        density_level = classify_density(density_ratio)

        in_flow = incoming_flow[zone_id]
        out_flow = outgoing_flow[zone_id]
        net = in_flow - out_flow

        risk_score = compute_risk_score(density_ratio, in_flow, capacity)
        risk_level = classify_risk(risk_score)

        bottleneck = detect_bottleneck(
            zone_id, risk_level, density_ratio, in_flow, net
        )

        zone_dict = {
            "zone_id": zone_id,
            "people": people,
            "capacity": capacity,
            "occupancy_ratio": density_ratio,
            "density_ratio": density_ratio,
            "density_percent": density_percent,
            "density_level": density_level,
            "incoming_flow": in_flow,
            "outgoing_flow": out_flow,
            "net_flow": net,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "is_bottleneck": bottleneck["is_bottleneck"],
        }
        zones.append(zone_dict)

        if bottleneck["is_bottleneck"]:
            bottlenecks.append(bottleneck)

    result = {
        "zones": zones,
        "bottlenecks": bottlenecks,
    }

    # Store as the live intelligence state
    set_live_intelligence_state(result)

    return result


# ===================================================================
# Live state management
# ===================================================================

def get_live_intelligence_state() -> dict:
    """Return the most recent crowd intelligence state.

    If no observed track data has been analysed yet, returns an empty
    default state.
    """
    global _current_intelligence_state
    if _current_intelligence_state is None:
        return _empty_state()
    return _current_intelligence_state


def set_live_intelligence_state(state: dict) -> None:
    """Replace the in-memory intelligence state."""
    global _current_intelligence_state
    _current_intelligence_state = state


# ===================================================================
# Simulation adapter
# ===================================================================

def simulation_to_tracks(simulation_state: dict) -> list[dict]:
    """Convert a ``crowd_service.simulate_crowd()`` output into track
    observations that ``analyze_tracks()`` can consume.

    This is an adapter/helper so the simulation can later feed the same
    intelligence layer.  It creates synthetic track IDs from the
    simulated zone populations.

    Parameters
    ----------
    simulation_state : dict
        Output from ``simulate_crowd()``.  Must contain ``"zones"`` with
        each zone having ``zone_id`` and ``people``.

    Returns
    -------
    list[dict]
        List of track observations suitable for ``analyze_tracks()``.
    """
    tracks: list[dict] = []
    global_counter = 0

    for zone in simulation_state.get("zones", []):
        zone_id = zone["zone_id"]
        people = zone.get("people", 0)

        for _ in range(people):
            tracks.append({
                "track_id": f"SIM_{global_counter:06d}",
                "zone_id": zone_id,
                "timestamp": 0.0,
            })
            global_counter += 1

    return tracks


# ===================================================================
# Helpers
# ===================================================================

def _empty_state() -> dict:
    """Return a clean empty/default intelligence state."""
    zones = []
    for zone_id, _, capacity in ZONE_DEFINITIONS:
        zones.append({
            "zone_id": zone_id,
            "people": 0,
            "capacity": capacity,
            "occupancy_ratio": 0.0,
            "density_ratio": 0.0,
            "density_percent": 0.0,
            "density_level": "LOW",
            "incoming_flow": 0,
            "outgoing_flow": 0,
            "net_flow": 0,
            "risk_score": 0.0,
            "risk_level": "LOW",
            "is_bottleneck": False,
        })
    return {
        "zones": zones,
        "bottlenecks": [],
    }
