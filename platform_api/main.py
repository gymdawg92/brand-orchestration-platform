import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response

from platform_api.database import create_db_and_tables
from platform_api.logging_config import setup_logging
from platform_api.metrics import REQUEST_COUNT, REQUEST_LATENCY
from platform_api.routers import agents, brands, health, metrics_router, tasks

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Brand Orchestration Platform",
    version="0.1.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def log_and_measure(request: Request, call_next):
    trace_id = str(uuid.uuid4())
    request.state.trace_id = trace_id
    start = time.monotonic()
    response: Response = await call_next(request)
    duration_ms = round((time.monotonic() - start) * 1000, 1)

    logger.info(
        "request",
        extra={
            "brand_id": request.path_params.get("slug", ""),
            "task_type": "",
            "trace_id": trace_id,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )
    REQUEST_COUNT.labels(
        method=request.method,
        path=request.url.path,
        status=str(response.status_code),
    ).inc()
    REQUEST_LATENCY.labels(path=request.url.path).observe(duration_ms / 1000)
    return response


app.include_router(health.router)
app.include_router(metrics_router.router)
app.include_router(brands.router)
app.include_router(agents.router)
app.include_router(tasks.router)
