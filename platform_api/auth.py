import hashlib
from typing import Optional

from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlmodel import Session, select

from platform_api.database import get_session
from platform_api.models.brand import Brand

api_key_header = APIKeyHeader(name="X-Brand-API-Key", auto_error=False)


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()


def get_brand_from_api_key(
    slug: str,
    api_key: Optional[str] = Security(api_key_header),
    session: Session = Depends(get_session),
) -> Brand:
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing X-Brand-API-Key header")
    brand = session.exec(select(Brand).where(Brand.slug == slug)).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    if brand.api_key_hash != hash_api_key(api_key):
        raise HTTPException(status_code=403, detail="Invalid API key")
    return brand
