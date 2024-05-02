import uuid

from .models import BaseUser, BaseRole
from ..generics.utils.partial import optional


class UserCreate(BaseUser):
    password: str 

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

