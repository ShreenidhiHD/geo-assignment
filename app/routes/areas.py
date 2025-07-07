from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from geoalchemy2.functions import ST_Contains, ST_Area, ST_Intersects
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import Polygon
from typing import List
from ..database import get_session
from ..models import Area, AreaCreate, AreaResponse, Location

router = APIRouter(prefix="/areas", tags=["areas"])

@router.post("/", response_model=AreaResponse)
def create_area(area: AreaCreate, session: Session = Depends(get_session)):
    # Create geometry from coordinates
    polygon = Polygon(area.coordinates[0])
    geometry = from_shape(polygon, srid=4326)
    
    db_area = Area(
        name=area.name,
        description=area.description,
        geometry=geometry
    )
    session.add(db_area)
    session.commit()
    session.refresh(db_area)
    
    return AreaResponse(
        id=db_area.id,
        name=db_area.name,
        description=db_area.description
    )

@router.get("/", response_model=List[AreaResponse])
def get_areas(session: Session = Depends(get_session)):
    areas = session.exec(select(Area)).all()
    
    return [
        AreaResponse(
            id=area.id,
            name=area.name,
            description=area.description
        )
        for area in areas
    ]

@router.get("/{area_id}", response_model=AreaResponse)
def get_area(area_id: int, session: Session = Depends(get_session)):
    area = session.get(Area, area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    
    return AreaResponse(
        id=area.id,
        name=area.name,
        description=area.description
    )

@router.get("/{area_id}/locations")
def get_locations_in_area(area_id: int, session: Session = Depends(get_session)):
    area = session.get(Area, area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    
    locations = session.exec(
        select(Location).where(ST_Contains(area.geometry, Location.geometry))
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

@router.put("/{area_id}", response_model=AreaResponse)
def update_area(area_id: int, area: AreaCreate, session: Session = Depends(get_session)):
    db_area = session.get(Area, area_id)
    if not db_area:
        raise HTTPException(status_code=404, detail="Area not found")
    
    # Update geometry from new coordinates
    polygon = Polygon(area.coordinates[0])
    geometry = from_shape(polygon, srid=4326)
    
    db_area.name = area.name
    db_area.description = area.description
    db_area.geometry = geometry
    
    session.add(db_area)
    session.commit()
    session.refresh(db_area)
    
    return AreaResponse(
        id=db_area.id,
        name=db_area.name,
        description=db_area.description
    )

@router.delete("/{area_id}")
def delete_area(area_id: int, session: Session = Depends(get_session)):
    area = session.get(Area, area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    
    session.delete(area)
    session.commit()
    
    return {"message": "Area deleted successfully"}
