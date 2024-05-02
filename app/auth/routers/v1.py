from datetime import timedelta
from jwt import DecodeError, ExpiredSignatureError, MissingRequiredClaimError

from fastapi import APIRouter, status, HTTPException, Body

from ..schemas import Token, LoginRequest, RefreshToken
from ...users.crud import user_crud
from ...generics import settings
from ...generics.utils import security


auth_v1 = APIRouter(prefix='/auth')


@auth_v1.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(body: LoginRequest):
    user = await user_crud.authenticate(email=body.email, password=body.password)
    if not user:
        raise HTTPException(status_code=400, detail="Email or Password incorrect")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="User is inactive")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    refresh_token = security.create_refresh_token(
        user.id, expires_delta=refresh_token_expires
    )
    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )


@auth_v1.post("/jwt/refresh", status_code=201, response_model=Token)
async def get_new_access_token(
    body: RefreshToken = Body(...),
):
    try:
        payload = security.decode_token(body.refresh_token)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your token has expired. Please log in again.",
        )
    except DecodeError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Error when decoding the token. Please check your request.",
        )
    except MissingRequiredClaimError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="There is no required field in your token. Please contact the administrator.",
        )

    if payload["type"] != "refresh": raise
    user_id = payload["sub"]
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(user_id, expires_delta=access_token_expires)
    refresh_token = security.create_refresh_token(user_id, expires_delta=refresh_token_expires)
    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )