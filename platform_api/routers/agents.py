import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from platform_api.auth import get_brand_from_api_key
from platform_api.database import get_session
from platform_api.models.brand import Brand
from platform_api.models.brand_agent import BrandAgent, BrandAgentCreate, BrandAgentRead

router = APIRouter(prefix="/brands/{slug}/agents", tags=["agents"])


@router.post("", response_model=BrandAgentRead, status_code=201)
def register_agent(
    slug: str,
    body: BrandAgentCreate,
    brand: Brand = Depends(get_brand_from_api_key),
    session: Session = Depends(get_session),
):
    agent = BrandAgent(brand_id=brand.id, **body.dict())
    session.add(agent)
    session.commit()
    session.refresh(agent)
    return agent


@router.delete("/{agent_id}", status_code=204)
def unregister_agent(
    slug: str,
    agent_id: uuid.UUID,
    brand: Brand = Depends(get_brand_from_api_key),
    session: Session = Depends(get_session),
):
    agent = session.exec(
        select(BrandAgent).where(
            BrandAgent.id == agent_id,
            BrandAgent.brand_id == brand.id,
        )
    ).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    session.delete(agent)
    session.commit()
