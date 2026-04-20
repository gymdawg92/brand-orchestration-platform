from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from platform_api.auth import hash_api_key
from platform_api.database import get_session
from platform_api.models.brand import Brand, BrandCreate, BrandPatch, BrandRead
from platform_api.models.brand_agent import BrandAgent

router = APIRouter(prefix="/brands", tags=["brands"])


@router.post("", response_model=BrandRead, status_code=201)
def create_brand(body: BrandCreate, session: Session = Depends(get_session)):
    if session.exec(select(Brand).where(Brand.slug == body.slug)).first():
        raise HTTPException(status_code=409, detail="Slug already exists")
    brand = Brand(
        slug=body.slug,
        name=body.name,
        status=body.status,
        config=body.config,
        api_key_hash=hash_api_key(body.api_key),
    )
    session.add(brand)
    session.commit()
    session.refresh(brand)
    return brand


@router.get("/{slug}", response_model=BrandRead)
def get_brand(slug: str, session: Session = Depends(get_session)):
    brand = session.exec(select(Brand).where(Brand.slug == slug)).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand


@router.patch("/{slug}", response_model=BrandRead)
def patch_brand(slug: str, body: BrandPatch, session: Session = Depends(get_session)):
    brand = session.exec(select(Brand).where(Brand.slug == slug)).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    for field, value in body.dict(exclude_unset=True).items():
        setattr(brand, field, value)
    brand.updated_at = datetime.utcnow()
    session.add(brand)
    session.commit()
    session.refresh(brand)
    return brand


@router.delete("/{slug}", status_code=204)
def delete_brand(slug: str, session: Session = Depends(get_session)):
    brand = session.exec(select(Brand).where(Brand.slug == slug)).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    for agent in session.exec(
        select(BrandAgent).where(BrandAgent.brand_id == brand.id)
    ).all():
        session.delete(agent)
    session.delete(brand)
    session.commit()
