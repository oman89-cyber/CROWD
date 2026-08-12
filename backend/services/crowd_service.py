"""Crowd simulation service — deterministic crowd state generation.

Generates synthetic but internally consistent crowd distributions across
venue zones for each event phase.  The same (crowd_size, event_phase) input
always produces the same output — critical for reliable demo scenarios.

This module is deliberately independent from the route engine.  Crowd-aware
routing will consume crowd state in a later step; this service does NOT
modify edge costs or touch NetworkX.
"""

from __future__ import annotations

from typing import Optional

# ---------------------------------------------------------------------------
# Zone definitions — derived from venue.json (excludes parking & individual
# seats, which are not crowd-density zones).
# ---------------------------------------------------------------------------

# Each zone: (zone_id, zone_type, capacity)
ZONE_DEFINITIONS: list[tuple[str, str, int]] = [
    # Gates
    ("GATE_A",      "gate",     3000),
    ("GATE_B",      "gate",     3000),
    ("GATE_C",      "gate",     3000),
    ("GATE_D",      "gate",     3000),
    # Corridors
    ("CORRIDOR_A",  "corridor", 5000),
    ("CORRIDOR_B",  "corridor", 5000),
    ("CORRIDOR_C",  "corridor", 5000),
    ("CORRIDOR_D",  "corridor", 5000),
    # Seating blocks
    ("BLOCK_A",     "block",    8000),
    ("BLOCK_B",     "block",    8000),
    ("BLOCK_C",     "block",    8000),
    ("BLOCK_D",     "block",    8000),
    # Food courts
    ("FOOD_A",      "food",     1500),
    ("FOOD_B",      "food",     1500),
    # Washrooms
    ("WASHROOM_A",  "washroom", 800),
    ("WASHROOM_B",  "washroom", 800),
    ("WASHROOM_C",  "washroom", 800),
    ("WASHROOM_D",  "washroom", 800),
    # Exits
    ("EXIT_A",      "exit",     4000),
    ("EXIT_B",      "exit",     4000),
]

# ---------------------------------------------------------------------------
# Phase distribution tables
# ---------------------------------------------------------------------------
# Each table maps zone_type → (crowd_share, incoming_flow_pct, outgoing_flow_pct)
#
# crowd_share:       fraction of crowd_size that goes to zones of this type
#                    (will be divided equally among zones of the same type)
# incoming_flow_pct: synthetic incoming flow as % of zone people
# outgoing_flow_pct: synthetic outgoing flow as % of zone people
#
# The shares do NOT need to sum to exactly 1.0 — they are normalised at
# runtime so the total distributed exactly equals crowd_size.

_PHASE_DISTRIBUTIONS: dict[str, dict[str, tuple[float, float, float]]] = {
    "ENTRY": {
        #              share   in_flow%  out_flow%
        "gate":       (0.35,   0.15,     0.05),
        "corridor":   (0.25,   0.10,     0.08),
        "block":      (0.15,   0.08,     0.02),
        "food":       (0.05,   0.03,     0.02),
        "washroom":   (0.04,   0.02,     0.02),
        "exit":       (0.02,   0.01,     0.01),
    },
    "PRE_EVENT": {
        "gate":       (0.08,   0.03,     0.10),
        "corridor":   (0.20,   0.08,     0.10),
        "block":      (0.55,   0.12,     0.02),
        "food":       (0.06,   0.04,     0.03),
        "washroom":   (0.04,   0.03,     0.03),
        "exit":       (0.01,   0.01,     0.01),
    },
    "HALFTIME": {
        "gate":       (0.03,   0.01,     0.02),
        "corridor":   (0.25,   0.12,     0.10),
        "block":      (0.30,   0.04,     0.08),
        "food":       (0.18,   0.10,     0.06),
        "washroom":   (0.12,   0.08,     0.06),
        "exit":       (0.04,   0.02,     0.02),
    },
    "EXIT": {
        "gate":       (0.10,   0.05,     0.12),
        "corridor":   (0.25,   0.10,     0.12),
        "block":      (0.10,   0.02,     0.15),
        "food":       (0.03,   0.02,     0.05),
        "washroom":   (0.03,   0.02,     0.04),
        "exit":       (0.35,   0.15,     0.05),
    },
}

VALID_PHASES = list(_PHASE_DISTRIBUTIONS.keys())

# ---------------------------------------------------------------------------
# In-memory crowd state (for GET /api/crowd/live)
# ---------------------------------------------------------------------------
_current_crowd_state: Optional[dict] = None


def _count_zones_by_type() -> dict[str, int]:
    """Return how many zones exist per zone_type."""
    counts: dict[str, int] = {}
    for _, ztype, _ in ZONE_DEFINITIONS:
        counts[ztype] = counts.get(ztype, 0) + 1
    return counts


def simulate_crowd(crowd_size: int, event_phase: str) -> dict:
    """Generate a deterministic crowd state for the given parameters.

    Parameters
    ----------
    crowd_size : int
        Total number of people in the venue.
    event_phase : str
        One of ``ENTRY``, ``PRE_EVENT``, ``HALFTIME``, ``EXIT``.

    Returns
    -------
    dict
        Structured crowd state with ``total_people``, ``event_phase``, and
        a ``zones`` list.
    """
    phase = event_phase.upper()
    if phase not in _PHASE_DISTRIBUTIONS:
        raise ValueError(
            f"Unknown event_phase '{event_phase}'. "
            f"Valid phases: {VALID_PHASES}"
        )

    dist = _PHASE_DISTRIBUTIONS[phase]
    type_counts = _count_zones_by_type()

    # --- Step 1: compute raw per-zone people (before normalisation) --------
    raw: list[tuple[str, str, int, float]] = []  # (zone_id, type, cap, raw_people)
    total_raw = 0.0
    for zone_id, ztype, capacity in ZONE_DEFINITIONS:
        share, _, _ = dist[ztype]
        n_zones = type_counts[ztype]
        zone_people = (share / n_zones) * crowd_size
        raw.append((zone_id, ztype, capacity, zone_people))
        total_raw += zone_people

    # --- Step 2: normalise so sum == crowd_size exactly --------------------
    if total_raw == 0:
        scale = 0.0
    else:
        scale = crowd_size / total_raw

    int_people: list[int] = []
    for _, _, _, rp in raw:
        int_people.append(int(rp * scale))

    # Distribute rounding remainder to the largest zones first
    remainder = crowd_size - sum(int_people)
    if remainder != 0:
        # Sort zone indices by descending raw people; deterministic tie-break
        # by index.
        indices = sorted(
            range(len(raw)),
            key=lambda i: (-raw[i][3], i),
        )
        for i in range(abs(remainder)):
            idx = indices[i % len(indices)]
            int_people[idx] += 1 if remainder > 0 else -1

    # --- Step 3: build zone dicts -----------------------------------------
    zones: list[dict] = []
    for i, (zone_id, ztype, capacity, _) in enumerate(raw):
        people = max(0, int_people[i])
        density = round(min(people / capacity, 1.0), 4) if capacity > 0 else 0.0
        _, in_pct, out_pct = dist[ztype]

        incoming_flow = int(people * in_pct)
        outgoing_flow = int(people * out_pct)

        zones.append({
            "zone_id": zone_id,
            "people": people,
            "capacity": capacity,
            "density": density,
            "incoming_flow": incoming_flow,
            "outgoing_flow": outgoing_flow,
            "risk": 0.0,
        })

    return {
        "total_people": crowd_size,
        "event_phase": phase,
        "zones": zones,
    }


# ---------------------------------------------------------------------------
# Live state management
# ---------------------------------------------------------------------------

def get_live_crowd_state() -> dict:
    """Return the current in-memory crowd state.

    If no simulation has been run yet, returns a default ENTRY scenario
    with 40 000 attendees.
    """
    global _current_crowd_state
    if _current_crowd_state is None:
        _current_crowd_state = simulate_crowd(40000, "ENTRY")
    return _current_crowd_state


def set_live_crowd_state(state: dict) -> None:
    """Replace the in-memory crowd state (called after a simulation)."""
    global _current_crowd_state
    _current_crowd_state = state
