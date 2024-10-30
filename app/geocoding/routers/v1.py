import uuid

from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse

import elasticsearch

from ..services import GeocodingService

geocoding_v1 = APIRouter(prefix='/geocoding')


@geocoding_v1.get('/search', status_code=status.HTTP_200_OK)
async def search(geocoding_svc: GeocodingService, query: str, limit: int = 5):
    result = await geocoding_svc.auto_complete(query, limit)
    return JSONResponse(content=result)


@geocoding_v1.get('/reverse', status_code=status.HTTP_200_OK)
async def to_latlon(lat: float, lon: float, geocoding_svc: GeocodingService):
    result = await geocoding_svc.search_by_coordinate(lat, lon)
    return JSONResponse(content=result)


@geocoding_v1.get('/{location_id}', status_code=status.HTTP_200_OK)
async def get_by_id(location_id: uuid.UUID, geocoding_svc: GeocodingService):
    try:
        result = await geocoding_svc.get_by_id(location_id)
    except elasticsearch.NotFoundError:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
    return JSONResponse(content=result)


