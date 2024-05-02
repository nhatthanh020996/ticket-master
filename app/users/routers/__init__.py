from fastapi import APIRouter

from .v1 import user_router_v1, role_router_v1

user_router = APIRouter(prefix='/api', tags=['USER'])
user_router.include_router(user_router_v1, prefix='/v1')
user_router.include_router(role_router_v1, prefix='/v1')