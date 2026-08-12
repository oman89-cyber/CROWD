from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base, SessionLocal
from api.tickets import router as tickets_router
from api.routes import router as routes_router
from api.crowd import router as crowd_router
from api.intelligence import router as intelligence_router
from services.ticket_service import seed_tickets


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema and seed demo tickets
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_tickets(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="CrowdShield AI Backend",
    description="Backend API for CrowdShield AI platform",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware configuration for local Next.js development
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(tickets_router)
app.include_router(routes_router)
app.include_router(crowd_router)
app.include_router(intelligence_router)


@app.get("/")
def read_root():
    return {"message": "CrowdShield AI Backend"}


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "crowdshield-backend",
    }
