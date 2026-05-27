from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.models.domain import CustomerSegment, Product, StockMovement, StockMovementType


def demand_forecast(db: Session) -> list[dict[str, int | float | str]]:
    products = db.scalars(select(Product).order_by(Product.name)).all()
    forecasts = []
    for product in products:
        recent_sales = db.scalar(
            select(func.coalesce(func.sum(StockMovement.quantity), 0)).where(
                StockMovement.product_id == product.id,
                StockMovement.movement_type == StockMovementType.sale,
            )
        )
        baseline = int(recent_sales or max(product.reorder_quantity * 0.35, product.reorder_point))
        forecasts.append(
            {
                "product_id": product.id,
                "sku": product.sku,
                "product_name": product.name,
                "expected_30_day_demand": max(1, baseline),
                "confidence": 0.68 if recent_sales else 0.45,
                "method": "movement-history-baseline",
            }
        )
    return forecasts


def customer_insights(db: Session) -> dict[str, int | float | list[dict[str, str | int | float]]]:
    total = db.scalar(select(func.count(CustomerSegment.id))) or 0
    churn = db.scalar(select(func.count(CustomerSegment.id)).where(CustomerSegment.churn_label == 1)) or 0
    high_value = (
        db.scalar(select(func.count(CustomerSegment.id)).where(CustomerSegment.monetary >= 1000)) or 0
    )
    region_rows = db.execute(
        select(CustomerSegment.region, func.count(CustomerSegment.id), func.avg(CustomerSegment.monetary))
        .group_by(CustomerSegment.region)
        .order_by(desc(func.count(CustomerSegment.id)))
        .limit(5)
    ).all()
    return {
        "total_customers": total,
        "churn_rate": round(churn / total, 4) if total else 0,
        "high_value_customers": high_value,
        "top_regions": [
            {"region": region, "customers": count, "avg_monetary": round(float(avg or 0), 2)}
            for region, count, avg in region_rows
        ],
    }
