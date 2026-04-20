import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class BrandAgent(SQLModel, table=True):
    __tablename__ = "brand_agents"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    brand_id: uuid.UUID = Field(foreign_key="brands.id", index=True)
    task_type: str
    agent_ref: str
    priority: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BrandAgentCreate(SQLModel):
    task_type: str
    agent_ref: str
    priority: int = 0


class BrandAgentRead(SQLModel):
    id: uuid.UUID
    brand_id: uuid.UUID
    task_type: str
    agent_ref: str
    priority: int
    created_at: datetime
