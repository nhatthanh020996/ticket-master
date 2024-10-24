from fastapi import APIRouter

from .v1 import geocoding_v1 

geocoding_router = APIRouter(prefix='/api', tags=['GEOCODING'])
geocoding_router.include_router(geocoding_v1, prefix='/v1')