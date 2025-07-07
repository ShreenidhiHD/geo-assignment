from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from geoalchemy2.functions import ST_Contains, ST_Distance, ST_DWithin
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import Point
from typing import List, Optional
from ..database import get_session
from ..models import Location, LocationCreate, LocationResponse, Area

router = APIRouter(prefix="/locations", tags=["locations"])

@router.post("/", response_model=LocationResponse)
def create_location(location: LocationCreate, session: Session = Depends(get_session)):
    # Create geometry from coordinates
    point = Point(location.longitude, location.latitude)
    geometry = from_shape(point, srid=4326)
    
    db_location = Location(
        name=location.name,
        latitude=location.latitude,
        longitude=location.longitude,
        geometry=geometry
    )
    session.add(db_location)
    session.commit()
    session.refresh(db_location)
    
    return LocationResponse(
        id=db_location.id,
        name=db_location.name,
        latitude=db_location.latitude,
        longitude=db_location.longitude
    )

@router.get("/", response_model=List[LocationResponse])
def get_locations(
    session: Session = Depends(get_session),
    area_id: Optional[int] = Query(None, description="Filter locations within a specific area"),
    latitude: Optional[float] = Query(None, description="Center latitude for proximity search"),
    longitude: Optional[float] = Query(None, description="Center longitude for proximity search"),
    radius: Optional[float] = Query(None, description="Search radius in kilometers")
):
    query = select(Location)
    
    if area_id:
        area = session.get(Area, area_id)
        if not area:
            raise HTTPException(status_code=404, detail="Area not found")
        query = query.where(ST_Contains(area.geometry, Location.geometry))
    
    if latitude and longitude and radius:
        center_point = from_shape(Point(longitude, latitude), srid=4326)
        query = query.where(ST_DWithin(Location.geometry, center_point, radius * 1000))
    
    locations = session.exec(query).all()
    
    return [
        LocationResponse(
            id=loc.id,
            name=loc.name,
            latitude=loc.latitude,
            longitude=loc.longitude
        )
        for loc in locations
    ]

@router.get("/{location_id}", response_model=LocationResponse)
def get_location(location_id: int, session: Session = Depends(get_session)):
    location = session.get(Location, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    return LocationResponse(
        id=location.id,
        name=location.name,
        latitude=location.latitude,
        longitude=location.longitude
    )

@router.put("/{location_id}", response_model=LocationResponse)
def update_location(location_id: int, location: LocationCreate, session: Session = Depends(get_session)):
    db_location = session.get(Location, location_id)
    if not db_location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Update geometry from new coordinates
    point = Point(location.longitude, location.latitude)
    geometry = from_shape(point, srid=4326)
    
    db_location.name = location.name
    db_location.latitude = location.latitude
    db_location.longitude = location.longitude
    db_location.geometry = geometry
    
    session.add(db_location)
    session.commit()
    session.refresh(db_location)
    
    return LocationResponse(
        id=db_location.id,
        name=db_location.name,
        latitude=db_location.latitude,
        longitude=db_location.longitude
    )

@router.delete("/{location_id}")
def delete_location(location_id: int, session: Session = Depends(get_session)):
    location = session.get(Location, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    session.delete(location)
    session.commit()
    
    return {"message": "Location deleted successfully"}
