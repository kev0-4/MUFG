from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.config.settings import settings
from app.api.financial import router as financial_router
from app.utils.logger import setup_logging, log_metadata

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    setup_logging()
    log_metadata({
        "function": "startup",
        "status": "success",
        "debug_mode": settings.debug,
        "mock_data": settings.mock_data_enabled
    })
    
    yield
    
    # Shutdown
    log_metadata({
        "function": "shutdown", 
        "status": "success"
    })

# Create FastAPI app
app = FastAPI(
    title="FinGuard Financial Data Server",
    description="Financial data integration server for FinGuard platform",
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(financial_router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "FinGuard Financial Data Server",
        "version": "1.0.0", 
        "status": "operational",
        "docs": "/docs",
        "mock_data": settings.mock_data_enabled
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
