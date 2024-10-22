import uuid
from typing import Optional
from pydantic import EmailStr
from datetime import datetime

from sqlmodel import BigInteger, Field, SQLModel, Relationship, Column, DateTime, String
from sqlalchemy_utils import ChoiceType
import sqlalchemy as sa

from ..generics import BaseUUIDPrimaryModel, BaseIntPrimaryKeyModel
from .enums import IGenderEnum

class BaseUser(SQLModel):
    username: str = Field(unique=True)
    email: EmailStr = Field(sa_column=Column(String, unique=True))
    role_id: int = Field(foreign_key='roles.id')
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False, nullable=True)
    phone: str | None = None
    gender: IGenderEnum | None = Field(
        default=IGenderEnum.other,
        sa_column=Column(ChoiceType(IGenderEnum, impl=String())),
    )
    birthdate: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )


class User(BaseUUIDPrimaryModel, BaseUser, table=True):
    __tablename__ = 'users'

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


class APIkey(SQLModel, table=True):
    __tablename__ = 'api_keys'
    
    id: int | None = Field(
        default=None,
        primary_key=True,
        index=True
    )
    key: str = Field(nullable=False)
    user_id: uuid.UUID = Field(foreign_key='users.id')
    user: User = Relationship(sa_relationship_kwargs={"lazy": "selectin"})
    is_disabled: bool = Field(default=False)
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=sa.text('now()'))
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'))    
    )
    