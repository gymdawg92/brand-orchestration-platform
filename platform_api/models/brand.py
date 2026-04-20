import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

import sqlalchemy as sa
from sqlmodel import Column, Field, SQLModel


class BrandStatus(str, Enum):
    active = "active"
    paused = "paused"
    archived = "archived"


class Brand(SQLModel, table=True):
    __tablename__ = "brands"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    slug: str = Field(unique=True, index=True)
    name: str
    status: BrandStatus = Field(default=BrandStatus.active)
    config: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(sa.JSON))
    api_key_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class BrandCreate(SQLModel):
    slug: str
    name: str
    status: BrandStatus = BrandStatus.active
    config: Optional[Dict[str, Any]] = None
    api_key: str


class BrandPatch(SQLModel):
    name: Optional[str] = None
    status: Optional[BrandStatus] = None
    config: Optional[Dict[str, Any]] = None


class BrandRead(SQLModel):
    id: uuid.UUID
    slug: str
    name: str
    status: BrandStatus
    config: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
