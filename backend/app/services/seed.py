import csv
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import get_password_hash
from app.models.domain import Category, CustomerSegment, Product, StockItem, Supplier, User, Warehouse


def seed_database(db: Session) -> dict[str, int]:
    if db.scalar(select(User).where(User.email == "admin@inventory-nexus.example.com")) is None:
        db.add(
            User(
                email="admin@inventory-nexus.example.com",
                full_name="Inventory Nexus Admin",
                hashed_password=get_password_hash("ChangeMe123!"),
                role="admin",
            )
        )

    categories = _ensure_categories(db)
    suppliers = _ensure_suppliers(db)
    warehouses = _ensure_warehouses(db)
    products = _ensure_products(db, categories, suppliers)
    _ensure_stock(db, products, warehouses)
    customers_imported = _import_customer_mart(db)
    db.commit()
    return {"products": len(products), "customers_imported": customers_imported}


def _ensure_categories(db: Session) -> dict[str, Category]:
    names = ["Beauty", "Apparel", "Home", "Accessories", "Wellness"]
    result = {}
    for name in names:
        category = db.scalar(select(Category).where(Category.name == name))
        if category is None:
            category = Category(name=name, description=f"{name} inventory line")
            db.add(category)
            db.flush()
        result[name] = category
    return result


def _ensure_suppliers(db: Session) -> dict[str, Supplier]:
    specs = [
        ("Aster Supply Co", 8, 0.91),
        ("Northline Wholesale", 12, 0.84),
        ("Urban Retail Partners", 6, 0.88),
    ]
    result = {}
    for name, lead_time, reliability in specs:
        supplier = db.scalar(select(Supplier).where(Supplier.name == name))
        if supplier is None:
            supplier = Supplier(name=name, lead_time_days=lead_time, reliability_score=reliability)
            db.add(supplier)
            db.flush()
        result[name] = supplier
    return result


def _ensure_warehouses(db: Session) -> list[Warehouse]:
    specs = [("DXB-01", "Dubai Fulfillment", "Dubai", "UAE"), ("LHR-01", "Lahore DC", "Lahore", "Pakistan")]
    warehouses = []
    for code, name, city, country in specs:
        warehouse = db.scalar(select(Warehouse).where(Warehouse.code == code))
        if warehouse is None:
            warehouse = Warehouse(code=code, name=name, city=city, country=country)
            db.add(warehouse)
            db.flush()
        warehouses.append(warehouse)
    return warehouses


def _ensure_products(db: Session, categories: dict[str, Category], suppliers: dict[str, Supplier]) -> list[Product]:
    specs = [
        ("BTY-SER-001", "Hydrating Face Serum", "Beauty", "Aster Supply Co", 32.0, 14.5, 45, 180),
        ("APP-SCR-014", "Premium Modal Scarf", "Apparel", "Urban Retail Partners", 24.0, 9.2, 35, 140),
        ("HOM-CND-221", "Soy Candle Trio", "Home", "Northline Wholesale", 42.0, 19.0, 25, 90),
        ("ACC-TOT-102", "Canvas Market Tote", "Accessories", "Urban Retail Partners", 18.0, 6.7, 60, 220),
        ("WLN-TEA-018", "Herbal Wellness Tea", "Wellness", "Aster Supply Co", 16.0, 5.5, 80, 260),
    ]
    products = []
    for sku, name, category_name, supplier_name, price, cost, reorder_point, reorder_quantity in specs:
        product = db.scalar(select(Product).where(Product.sku == sku))
        if product is None:
            product = Product(
                sku=sku,
                name=name,
                description=f"Curated {category_name.lower()} product for omnichannel retail.",
                category_id=categories[category_name].id,
                supplier_id=suppliers[supplier_name].id,
                unit_price=price,
                unit_cost=cost,
                reorder_point=reorder_point,
                reorder_quantity=reorder_quantity,
            )
            db.add(product)
            db.flush()
        products.append(product)
    return products


def _ensure_stock(db: Session, products: list[Product], warehouses: list[Warehouse]) -> None:
    starting_quantities = [28, 112, 19, 245, 77]
    for product, quantity in zip(products, starting_quantities, strict=True):
        stock = db.scalar(
            select(StockItem).where(
                StockItem.product_id == product.id,
                StockItem.warehouse_id == warehouses[0].id,
            )
        )
        if stock is None:
            db.add(StockItem(product_id=product.id, warehouse_id=warehouses[0].id, quantity_on_hand=quantity))


def _import_customer_mart(db: Session) -> int:
    csv_path = Path(get_settings().seed_csv_path)
    if not csv_path.exists():
        return 0
    if db.scalar(select(CustomerSegment.id).limit(1)) is not None:
        return 0

    imported = 0
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            db.add(
                CustomerSegment(
                    external_customer_id=row["CustomerID"],
                    country=row["Country"],
                    region=row["Region"],
                    recency=int(row["Recency"]),
                    frequency=int(row["Frequency"]),
                    monetary=float(row["Monetary"]),
                    avg_order_value=float(row["AvgOrderValue"]),
                    churn_label=int(row["ChurnLabel"]),
                    total_items=float(row["TotalItems"]),
                    unique_products=int(row["UniqueProducts"]),
                    total_orders=int(row["TotalOrders"]),
                    customer_lifespan_days=int(row["CustomerLifespanDays"]),
                )
            )
            imported += 1
    return imported
