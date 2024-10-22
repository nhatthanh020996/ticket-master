from fastapi import Request, Response, APIRouter, status, Query, Depends
from fastapi.responses import JSONResponse
from fastapi_pagination import Page, Params

from ..schemas import UserCreate, UserRead, RoleCreate, RoleRead
from ..crud import user_crud, role_crud
from ..enums import IRoleEnum
from ...auth import dependences

user_router_v1 = APIRouter(prefix='/users')
role_router_v1 = APIRouter(prefix='/roles')

@user_router_v1.post(
    '',
    status_code=status.HTTP_201_CREATED,
    response_model=UserRead
)
async def create_user(new_user: UserCreate):
    return await user_crud.create(obj_in=new_user)


@user_router_v1.get(
    '',
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(dependences.require_permission([IRoleEnum.ADMIN, IRoleEnum.SUPER_ADMIN]))],
    response_model=Page.with_custom_options(size=Query(20, ge=1, le=500))[UserRead]
)
async def list_users(params: Params = Depends()):
    return await user_crud.get_multi_paginated(params=params)


@user_router_v1.get(
    '/profile',
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(dependences.require_authentication)],
    response_model=UserRead
)
async def get_user_profile(user_id = Depends(dependences.get_user_id)):
    return await user_crud.get(id=user_id)


@role_router_v1.post(
    '',
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(dependences.require_permission([IRoleEnum.SUPER_ADMIN]))],
    response_model=RoleRead
)
async def create_role(new_user: RoleCreate):
    return await role_crud.create(obj_in=new_user)



