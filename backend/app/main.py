import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.db.session import Base, engine
from app.models import domain  # noqa: F401


settings = get_settings()
Base.metadata.create_all(bind=engine)

logger = logging.getLogger("inventory-nexus.backend")
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        logger.info("%s %s -> %s", request.method, request.url.path, response.status_code)
        return response


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Production-grade inventory operations, analytics, and AI planning API.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestLoggingMiddleware)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


@app.get("/welcome", tags=["system"])
def welcome() -> dict[str, str]:
    return {"message": "Welcome to the Flask API Service!"}


@app.get("/status", tags=["system"])
def status() -> dict[str, str]:
    return {"status": "running"}
