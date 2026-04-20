from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from platform_api.metrics import metrics_registry

router = APIRouter(tags=["ops"])


@router.get("/metrics", response_class=PlainTextResponse)
def metrics():
    return PlainTextResponse(generate_latest(metrics_registry), media_type=CONTENT_TYPE_LATEST)
