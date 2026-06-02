from fastapi import APIRouter

from app.api.v1 import analytics, auth, inventory, superset

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(inventory.router)
api_router.include_router(analytics.router)
api_router.include_router(superset.router)
