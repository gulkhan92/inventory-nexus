from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.deps import DbSession, get_current_user
from app.models.domain import User
from app.schemas.domain import ProductCreate, ProductRead, StockMovementCreate, StockMovementRead
from app.services.inventory import create_product, list_products, record_stock_movement

router = APIRouter(prefix="/inventory", tags=["inventory"])
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("/products", response_model=list[ProductRead])
def products(db: DbSession, _: CurrentUser, search: str | None = None) -> list[ProductRead]:
    return list_products(db, search)


@router.post("/products", response_model=ProductRead, status_code=201)
def add_product(payload: ProductCreate, db: DbSession, _: CurrentUser) -> ProductRead:
    return create_product(db, payload)


@router.post("/movements", response_model=StockMovementRead, status_code=201)
def add_stock_movement(payload: StockMovementCreate, db: DbSession, _: CurrentUser) -> StockMovementRead:
    return record_stock_movement(db, payload)
