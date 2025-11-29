"""FastAPI application for IndexTTS microservice"""

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .routes import voices, extract, synthesize, health

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app lifecycle - startup and shutdown"""
    logger.info("IndexTTS API Service starting on port 5150...")
    yield
    logger.info("IndexTTS API Service shutting down...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    
    app = FastAPI(
        title="IndexTTS API",
        description="REST API for IndexTTS2 with emotion-tagged synthesis and voice cloning",
        version="0.2.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    
    # Add CORS middleware for integration with web UIs (Trivok, Home Assistant, etc.)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, restrict to specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Create main router
    api_router = APIRouter(prefix="/api", tags=["API"])
    
    # Include sub-routers
    api_router.include_router(health.router)
    api_router.include_router(voices.router)
    api_router.include_router(extract.router)
    api_router.include_router(synthesize.router)
    
    app.include_router(api_router)
    
    # Root endpoint
    @app.get("/", tags=["Info"])
    async def root():
        """Root endpoint with API information"""
        return {
            "service": "IndexTTS API",
            "version": "0.2.0",
            "status": "running",
            "docs": "http://localhost:5150/docs",
            "port": 5150,
        }
    
    return app


# Create the app instance
app = create_app()
