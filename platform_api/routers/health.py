from fastapi import APIRouter
from platform_api.config import BUILD_SHA

router = APIRouter(tags=["ops"])


@router.get("/health")
def health():
    return {"status": "ok", "build": BUILD_SHA}
