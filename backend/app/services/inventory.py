from collections import defaultdict

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.domain import Product, StockItem, StockMovement, StockMovementType, Supplier
from app.schemas.domain import ProductCreate, ProductRead, StockMovementCreate


def list_products(db: Session, search: str | None = None) -> list[ProductRead]:
    statement = select(Product).options(
        joinedload(Product.category),
        joinedload(Product.supplier),
        joinedload(Product.stock_items),
    )
    if search:
        statement = statement.where(Product.name.ilike(f"%{search}%") | Product.sku.ilike(f"%{search}%"))
    products = db.scalars(statement.order_by(Product.name)).unique().all()
    return [_product_to_read(product) for product in products]


def create_product(db: Session, payload: ProductCreate) -> ProductRead:
    exists = db.scalar(select(Product).where(Product.sku == payload.sku))
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="SKU already exists")
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return _product_to_read(product)


def record_stock_movement(db: Session, payload: StockMovementCreate) -> StockMovement:
    try:
        movement_type = StockMovementType(payload.movement_type)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Unsupported movement type") from exc

    stock_item = db.scalar(
        select(StockItem).where(
            StockItem.product_id == payload.product_id,
            StockItem.warehouse_id == payload.warehouse_id,
        )
    )
    if stock_item is None:
        stock_item = StockItem(product_id=payload.product_id, warehouse_id=payload.warehouse_id)
        db.add(stock_item)

    delta = payload.quantity if movement_type in {StockMovementType.receipt, StockMovementType.return_in} else -payload.quantity
    if movement_type == StockMovementType.adjustment:
        delta = payload.quantity
    next_quantity = stock_item.quantity_on_hand + delta
    if next_quantity < 0:
        raise HTTPException(status_code=409, detail="Movement would make stock negative")
    stock_item.quantity_on_hand = next_quantity

    movement = StockMovement(
        product_id=payload.product_id,
        warehouse_id=payload.warehouse_id,
        movement_type=movement_type,
        quantity=payload.quantity,
        reference=payload.reference,
        note=payload.note,
    )
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return movement


def dashboard_metrics(db: Session) -> dict[str, int | float]:
    total_skus = db.scalar(select(func.count(Product.id))) or 0
    stock_rows = db.execute(
        select(Product.unit_cost, StockItem.quantity_on_hand, StockItem.quantity_reserved)
        .join(StockItem, StockItem.product_id == Product.id, isouter=True)
    ).all()
    inventory_value = sum((unit_cost or 0) * (qty or 0) for unit_cost, qty, _ in stock_rows)
    reserved_units = sum(reserved or 0 for _, _, reserved in stock_rows)
    low_stock_count = len(_low_stock_products(db))
    avg_supplier_reliability = db.scalar(select(func.avg(Supplier.reliability_score))) or 0
    return {
        "total_skus": total_skus,
        "inventory_value": round(inventory_value, 2),
        "low_stock_count": low_stock_count,
        "reserved_units": reserved_units,
        "churn_risk_customers": 0,
        "avg_supplier_reliability": round(float(avg_supplier_reliability), 2),
    }


def low_stock_recommendations(db: Session) -> list[dict[str, int | str]]:
    recommendations = []
    for product, current_stock in _low_stock_products(db):
        urgency = "critical" if current_stock <= max(5, product.reorder_point // 2) else "watch"
        recommendations.append(
            {
                "product_id": product.id,
                "sku": product.sku,
                "product_name": product.name,
                "current_stock": current_stock,
                "reorder_point": product.reorder_point,
                "recommended_quantity": product.reorder_quantity,
                "urgency": urgency,
                "rationale": (
                    f"On-hand stock is {current_stock}, below reorder point {product.reorder_point}. "
                    f"Supplier lead time is {product.supplier.lead_time_days} days."
                ),
            }
        )
    return recommendations


def _product_to_read(product: Product) -> ProductRead:
    quantity_on_hand = sum(item.quantity_on_hand for item in product.stock_items)
    quantity_reserved = sum(item.quantity_reserved for item in product.stock_items)
    return ProductRead(
        id=product.id,
        sku=product.sku,
        name=product.name,
        description=product.description,
        unit_price=product.unit_price,
        unit_cost=product.unit_cost,
        reorder_point=product.reorder_point,
        reorder_quantity=product.reorder_quantity,
        category_id=product.category_id,
        supplier_id=product.supplier_id,
        quantity_on_hand=quantity_on_hand,
        quantity_reserved=quantity_reserved,
        category_name=product.category.name if product.category else None,
        supplier_name=product.supplier.name if product.supplier else None,
    )


def _low_stock_products(db: Session) -> list[tuple[Product, int]]:
    quantities: dict[int, int] = defaultdict(int)
    for product_id, quantity in db.execute(select(StockItem.product_id, StockItem.quantity_on_hand)):
        quantities[product_id] += quantity
    products = db.scalars(select(Product).options(joinedload(Product.supplier))).all()
    return [(product, quantities[product.id]) for product in products if quantities[product.id] <= product.reorder_point]
