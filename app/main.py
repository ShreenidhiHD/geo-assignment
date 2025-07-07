from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .database import create_db_and_tables
from .routes.locations import router as locations_router
from .routes.areas import router as areas_router
from .routes.spatial import router as spatial_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(
    title="Geospatial API",
    description="a FastAPI application for managing geospatial data",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(locations_router)
app.include_router(areas_router)
app.include_router(spatial_router)

@app.get("/")
def root():
    return {"message": "Geospatial API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
