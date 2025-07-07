from sqlmodel import SQLModel, Field, Column
from geoalchemy2 import Geometry
from typing import Optional, List

class Location(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    latitude: float
    longitude: float
    geometry: Optional[str] = Field(default=None, sa_column=Column(Geometry('POINT', srid=4326)))

class Area(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    geometry: Optional[str] = Field(default=None, sa_column=Column(Geometry('POLYGON', srid=4326)))

class LocationCreate(SQLModel):
    name: str
    latitude: float
    longitude: float

class LocationResponse(SQLModel):
    id: int
    name: str
    latitude: float
    longitude: float

class AreaCreate(SQLModel):
    name: str
    description: Optional[str] = None
    coordinates: List[List[List[float]]]

class AreaResponse(SQLModel):
    id: int
    name: str
    description: Optional[str] = None
