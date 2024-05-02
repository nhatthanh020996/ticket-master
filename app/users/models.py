import uuid
from typing import Optional
from pydantic import EmailStr
from datetime import datetime

from sqlmodel import BigInteger, Field, SQLModel, Relationship, Column, DateTime, String
from sqlalchemy_utils import ChoiceType

from ..generics import BaseUUIDPrimaryModel, BaseIntPrimaryKeyModel
from .enums import IGenderEnum

class BaseUser(SQLModel):
    username: str = Field(unique=True)
    email: EmailStr = Field(sa_column=Column(String, unique=True))
    role_id: int = Field(foreign_key='roles.id')
    is_active: bool = Field(default=True)
    phone: str | None = None
    gender: IGenderEnum | None = Field(
        default=IGenderEnum.other,
        sa_column=Column(ChoiceType(IGenderEnum, impl=String())),
    )
    birthdate: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )


class User(BaseUUIDPrimaryModel, BaseUser, table=True):
    hashed_password: str | None = Field(default=None, nullable=False)
    role: Optional["Role"] = Relationship(  # noqa: F821
        back_populates="users", sa_relationship_kwargs={"lazy": "joined"}
    )


class BaseRole(SQLModel):
    name: str = Field(max_length=10)
    desc: Optional[str] = Field(default=None)

class Role(BaseIntPrimaryKeyModel, BaseRole, table=True):
    __tablename__ = 'roles'
    users: Optional[list["User"]] = Relationship(
        back_populates="role", sa_relationship_kwargs={"lazy": "selectin"}
    )