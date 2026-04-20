import logging
from typing import Any, Dict

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlmodel import Session, select

from platform_api.auth import get_brand_from_api_key
from platform_api.database import get_session
from platform_api.models.brand import Brand
from platform_api.models.brand_agent import BrandAgent

router = APIRouter(prefix="/brands/{slug}/tasks", tags=["tasks"])
logger = logging.getLogger(__name__)


class TaskRequest(BaseModel):
    task_type: str
    payload: Dict[str, Any] = {}


@router.post("")
async def dispatch_task(
    slug: str,
    body: TaskRequest,
    request: Request,
    brand: Brand = Depends(get_brand_from_api_key),
    session: Session = Depends(get_session),
):
    agent = session.exec(
        select(BrandAgent)
        .where(BrandAgent.brand_id == brand.id, BrandAgent.task_type == body.task_type)
        .order_by(BrandAgent.priority.desc())
    ).first()
    if not agent:
        raise HTTPException(
            status_code=422,
            detail=f"No agent registered for task_type={body.task_type!r}",
        )

    trace_id = getattr(request.state, "trace_id", "")
    dispatch_payload = {
        "brand_id": str(brand.id),
        "task_type": body.task_type,
        "payload": body.payload,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                agent.agent_ref,
                json=dispatch_payload,
                headers={"X-Trace-Id": trace_id},
            )
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as exc:
        logger.error(
            "agent_dispatch_error",
            extra={
                "brand_id": str(brand.id),
                "task_type": body.task_type,
                "trace_id": trace_id,
                "agent_ref": agent.agent_ref,
                "status_code": exc.response.status_code,
            },
        )
        raise HTTPException(status_code=502, detail="Agent returned an error")
    except httpx.RequestError as exc:
        logger.error(
            "agent_unreachable",
            extra={
                "brand_id": str(brand.id),
                "task_type": body.task_type,
                "trace_id": trace_id,
                "agent_ref": agent.agent_ref,
            },
        )
        raise HTTPException(status_code=503, detail="Agent unreachable")
