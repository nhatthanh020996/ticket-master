from typing import List
import uuid
import logging

from fastapi import Depends, HTTPException, status, Request
from sqlalchemy import select
from ..users.crud import user_crud
from ..generics import ASession
from ..generics.exceptions import InvalidCredentialsException, PermissionDeniedException
from ..generics.utils import security


logger = logging.getLogger(__name__)


async def require_authentication(request: Request, asession: ASession):
    authorization = request.headers.get("Authorization")
    if authorization is None:
        raise InvalidCredentialsException(message='Lacking token')
    _, _, token = authorization.partition(" ")
    try:
        payload = security.decode_token(token)
    except Exception:
        logger.exception('Invalid token')
        raise InvalidCredentialsException(message='Invalid Credentials')
    async with asession.begin() as session:
        user = await user_crud.get(id=uuid.UUID(payload['sub']), db_session=session)
    if user is None:
        raise InvalidCredentialsException(message='User does not exist')
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail='Account has been locked')
    request.state.user = {'id': user.id, 'role_id': user.role_id, 'username': user.username, 'is_active': user.is_active}
    return True


def require_permission(roles: List[int]):
    async def check_permission(request: Request, asession: ASession):
        await require_authentication(request, asession)
        role_id = request.state.user['role_id']
        if role_id in roles: return True
        raise PermissionDeniedException(message='Do not have permission to access this route')
    return check_permission


def get_user_id(request: Request):
    return request.state.user['id']
