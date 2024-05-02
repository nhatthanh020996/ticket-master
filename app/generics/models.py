import uuid
import pytz
from datetime import datetime

from sqlmodel import SQLModel, Field, Column, DateTime, UUID
import sqlalchemy as sa


class BaseIntPrimaryKeyModel(SQLModel):
    id: int | None = Field(
        default=None,
        primary_key=True,
        index=True
    )

    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=sa.text('now()'))
    )

    updated_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'))    
    )

class BaseUUIDPrimaryModel(SQLModel):
    id: uuid.UUID | None = Field(
        default=None,
        sa_column=Column(UUID, server_default=sa.text('gen_random_uuid()'), primary_key=True, index=True)
    )

    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=sa.text('now()'))
    )

    updated_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'))    
    )


