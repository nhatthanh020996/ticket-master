from fastapi import APIRouter

from .v1 import auth_v1 

auth_router = APIRouter(prefix='/api', tags=['AUTH'])
auth_router.include_router(auth_v1, prefix='/v1')