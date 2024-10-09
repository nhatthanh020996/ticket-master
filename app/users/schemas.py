import uuid

from sqlmodel import Field
from pydantic.json_schema import SkipJsonSchema

from .models import BaseUser, BaseRole
from ..generics.utils.partial import optional


class UserCreate(BaseUser):
    password: str
    is_verified: SkipJsonSchema[bool] = Field(default=False, nullable=True, exclude=True)
    is_active: SkipJsonSchema[bool] = Field(default=True, nullable=True, exclude=True)

    class Config:
        hashed_password = None


@optional
class UserUpdate(BaseUser):
    pass


class UserRead(BaseUser):
    id: uuid.UUID


class RoleCreate(BaseRole):
    pass

@optional
class RoleUpdate(BaseRole):
    pass

class RoleRead(BaseRole):
    id: int

