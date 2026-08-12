# CrowdShield AI

## Hackathon

Grand Prix Hackathon

## Problem Statement

PS3 — Crowd Flow Optimiser: Simulating and Rerouting Crowds in Real Time.

## Product

CrowdShield AI is an AI-powered crowd-flow intelligence platform for large venues.

The system has two sides:

1. User Portal
2. Organizer Control Center

## User Flow

Ticket ID / QR
→ Ticket verification
→ Gate / Parking / Seat identification
→ Personalized route
→ Venue entry
→ Anonymous crowd tracking
→ Current zone
→ Density-aware navigation
→ Destination selection
→ Crowd-aware rerouting

Possible destinations:

- Seat
- Food
- Washroom
- Merchandise
- Other

## Organizer Flow

Create event
→ Configure venue
→ Configure cameras
→ Upload ticket/event data
→ Define event schedule
→ Monitor live crowd
→ View zone density
→ View bottleneck prediction
→ Run what-if simulation
→ Generate recommended rerouting

## AI Pipeline

Camera / Video
→ Person Detection
→ Tracking
→ Zone Assignment
→ Crowd Density
→ Flow Analysis
→ Bottleneck Risk
→ Route Optimization

## Dark Zones

Camera-free areas are part of the long-term architecture and may use RF/Wi-Fi sensing.

For the 24-hour MVP, dark-zone sensing may be simulated.

## MVP Constraints

We have a 24-hour hackathon deadline.

Prioritize a working end-to-end system over production completeness.

Do NOT build initially:

- Native mobile app
- Real Wi-Fi radar hardware
- Facial recognition
- Real stadium deployment
- Complex authentication
- Payment
- VR
- Unnecessary microservices

## Required Demo

Ticket verification
→ Personalized route
→ Crowd detection
→ Zone density
→ Bottleneck prediction
→ Alternative route
→ Organizer simulation

## Team

Oman:
Frontend + Backend + AI/ML + Simulation + Integration

Pratyusha:
Frontend support / UX support

## Technology

Frontend:
Next.js
TypeScript
Tailwind CSS
React
SVG

Backend:
Python
FastAPI
SQLite for MVP
Pydantic

AI:
PyTorch
Hugging Face
OpenCV

Tracking:
ByteTrack or equivalent

Simulation:
Python
NumPy
NetworkX

Routing:
A* / Dijkstra with congestion-aware edge cost

Realtime:
WebSocket

## Identity Model

Do not depend on facial recognition.

Use:

Ticket ID
→ temporary session ID
→ anonymous tracking ID

The objective is to determine where attendees are and how to route them efficiently.

## Core Principle

The project must demonstrate an actual end-to-end connection between:

Frontend
→ Backend
→ AI / Simulation
→ Backend
→ Frontend