"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import auth, connections, history, migrations, schedules
from . import websocket


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup: create tables if needed
    from .database import Base, engine

    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown: cleanup if needed


app = FastAPI(
    title="MySQL Migration Tool",
    description="MySQL database migration tool with filtering support",
    version="0.1.0",
)

# Include routers
app.include_router(auth.router)
app.include_router(connections.router)
app.include_router(migrations.router)
app.include_router(history.router)
app.include_router(schedules.router)
app.include_router(websocket.router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
