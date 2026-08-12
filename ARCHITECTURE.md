# CrowdShield AI Architecture

## High-Level

User / Organizer Frontend
        ↓
      FastAPI
        ↓
 ┌──────┼───────────────┐
 ↓      ↓               ↓
Ticket Crowd         Simulation
Service Service       Service
        ↓               ↓
        AI/ML      Venue Graph
        ↓               ↓
 Detection          Bottleneck
 Tracking           Prediction
 Density             Routing
        └──────┬────────┘
               ↓
          Route Decision
               ↓
         Frontend Update

## Main Backend Services

### Ticket Service

Responsible for:

- ticket verification
- user session creation
- gate identification
- parking identification
- seat identification

### Crowd Service

Responsible for:

- current crowd state
- zone occupancy
- density
- flow

### ML Service

Responsible for:

- person detection
- tracking
- zone assignment
- crowd analysis
- bottleneck risk

### Simulation Service

Responsible for:

- venue graph
- simulated crowd movement
- bottleneck prediction
- route optimization

### Realtime Service

Responsible for:

- live crowd updates
- bottleneck alerts
- route changes

## Frontend

Two interfaces:

### User

Ticket
→ Route
→ Current Location
→ Destination
→ Navigation
→ Rerouting

### Organizer

Event
→ Venue
→ Cameras
→ Tickets
→ Live Crowd
→ Prediction
→ Simulation
→ Recommendation