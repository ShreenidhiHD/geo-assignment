# Geospatial API

FastAPI application for managing geospatial data with PostgreSQL and PostGIS.

## Setup

### Prerequisites
- Python 3.11+
- Poetry
- Docker and Docker Compose

### Installation

1. Install dependencies:
```bash
poetry shell
poetry install
```

2. Start the database:
```bash
docker-compose up -d db
```

3. Run the application:
```bash
python -m uvicorn app.main:app --reload
```

### Using Docker
```bash
docker-compose up --build
```

## API Endpoints

### Locations
- `POST /locations/` - Create location
- `GET /locations/` - List locations
- `GET /locations/{id}` - Get location
- `PUT /locations/{id}` - Update location
- `DELETE /locations/{id}` - Delete location

### Areas
- `POST /areas/` - Create area
- `GET /areas/` - List areas
- `GET /areas/{id}` - Get area
- `PUT /areas/{id}` - Update area
- `DELETE /areas/{id}` - Delete area

### Spatial Operations
- `GET /spatial/distance` - Calculate distance between points
- `GET /spatial/nearby` - Find nearby locations
- `GET /spatial/contains` - Check point in area
- `GET /spatial/intersections` - Find intersecting areas

## Database Configuration

Default connection:
- Host: localhost
- Port: 5433
- Database: spatialdb
- User: postgres
- Password: postgres

## Testing

Run the test suite:
```bash
python test_api.py
```
