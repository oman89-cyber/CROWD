# CrowdShield API Contract

## 1. Health

GET /health

Response:

{
  "status": "ok",
  "service": "crowdshield-backend"
}

---

## 2. Verify Ticket

POST /api/ticket/verify

Request:

{
  "ticket_id": "T0004"
}

Response:

{
  "valid": true,
  "session_id": "CS-1021",
  "gate": "C",
  "block": "C",
  "seat": "C124",
  "parking": "P3",
  "entry_window": "18:30-19:00"
}

---

## 3. Live Crowd

GET /api/crowd/live

Response:

{
  "total_people": 2841,
  "zones": [
    {
      "zone_id": "A",
      "people": 300,
      "capacity": 1000,
      "density": 0.30,
      "risk": 0.21
    }
  ]
}

---

## 4. Route

POST /api/route

Request:

{
  "session_id": "CS-1021",
  "destination": "SEAT_C124"
}

Response:

{
  "route": [
    "GATE_C",
    "CORRIDOR_2",
    "BLOCK_C",
    "SEAT_C124"
  ],
  "estimated_minutes": 8,
  "risk": 0.21
}

---

## 5. Simulation

POST /api/simulation

Request:

{
  "crowd_size": 40000,
  "event_phase": "HALFTIME"
}

Response:

{
  "bottlenecks": [
    {
      "zone": "ZONE_C",
      "risk": 0.92,
      "eta_minutes": 4
    }
  ]
}

---

## 6. Destination

POST /api/destination

Request:

{
  "session_id": "CS-1021",
  "destination_type": "WASHROOM"
}

Response:

{
  "destination": "WASHROOM_B",
  "estimated_minutes": 3,
  "risk": 0.18
}

---

## 7. Live Crowd WebSocket

/ws/crowd

Used for:

- crowd count
- zone density
- risk changes
- bottleneck alerts
- rerouting events