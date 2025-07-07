from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select
from geoalchemy2.functions import ST_Distance, ST_DWithin, ST_Contains, ST_Intersects
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from typing import List, Optional
from ..database import get_session
from ..models import Location, Area

router = APIRouter(prefix="/spatial", tags=["spatial"])

@router.get("/distance")
def calculate_distance(
    lat1: float = Query(..., description="Latitude of first point"),
    lon1: float = Query(..., description="Longitude of first point"),
    lat2: float = Query(..., description="Latitude of second point"),
    lon2: float = Query(..., description="Longitude of second point"),
    session: Session = Depends(get_session)
):
    point1 = from_shape(Point(lon1, lat1), srid=4326)
    point2 = from_shape(Point(lon2, lat2), srid=4326)
    
    result = session.exec(
        select(ST_Distance(point1, point2))
    ).first()
    
    return {"distance_meters": result}

@router.get("/nearby")
def find_nearby_locations(
    latitude: float = Query(..., description="Center latitude"),
    longitude: float = Query(..., description="Center longitude"),
    radius: float = Query(..., description="Search radius in kilometers"),
    session: Session = Depends(get_session)
):
    center_point = from_shape(Point(longitude, latitude), srid=4326)
    
    locations = session.exec(
        select(Location).where(
            ST_DWithin(Location.geometry, center_point, radius * 1000)
        )
    ).all()
    
    return [
        {
            "id": loc.id,
            "name": loc.name,
            "latitude": loc.latitude,
            "longitude": loc.longitude
        }
        for loc in locations
    ]

@router.get("/contains")
def check_point_in_area(
    area_id: int = Query(..., description="Area ID"),
    latitude: float = Query(..., description="Point latitude"),
    longitude: float = Query(..., description="Point longitude"),
    session: Session = Depends(get_session)
):
    area = session.get(Area, area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    
    point = from_shape(Point(longitude, latitude), srid=4326)
    
    result = session.exec(
        select(ST_Contains(area.geometry, point))
    ).first()
    
    return {
        "area_id": area_id,
        "area_name": area.name,
        "point": {"latitude": latitude, "longitude": longitude},
        "contains": result
    }

@router.get("/intersections")
def find_intersecting_areas(
    area_id: int = Query(..., description="Area ID to check intersections with"),
    session: Session = Depends(get_session)
):
    target_area = session.get(Area, area_id)
    if not target_area:
        raise HTTPException(status_code=404, detail="Area not found")
    
    intersecting_areas = session.exec(
        select(Area).where(
            ST_Intersects(Area.geometry, target_area.geometry)
        ).where(Area.id != area_id)
    ).all()
    
    return [
        {
            "id": area.id,
            "name": area.name,
            "description": area.description
        }
        for area in intersecting_areas
    ]
