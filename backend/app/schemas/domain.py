from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ProductBase(BaseModel):
    sku: str
    name: str
    description: str | None = None
    unit_price: float
    unit_cost: float
    reorder_point: int = 25
    reorder_quantity: int = 100
    category_id: int
    supplier_id: int


class ProductCreate(ProductBase):
    pass


class ProductRead(ProductBase):
    id: int
    quantity_on_hand: int = 0
    quantity_reserved: int = 0
    category_name: str | None = None
    supplier_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class StockMovementCreate(BaseModel):
    product_id: int
    warehouse_id: int
    movement_type: str
    quantity: int
    reference: str | None = None
    note: str | None = None


class StockMovementRead(StockMovementCreate):
    id: int
    occurred_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DashboardMetrics(BaseModel):
    total_skus: int
    inventory_value: float
    low_stock_count: int
    reserved_units: int
    churn_risk_customers: int
    avg_supplier_reliability: float


class ReorderRecommendation(BaseModel):
    product_id: int
    sku: str
    product_name: str
    current_stock: int
    reorder_point: int
    recommended_quantity: int
    urgency: str
    rationale: str


class DemandForecast(BaseModel):
    product_id: int
    sku: str
    product_name: str
    expected_30_day_demand: int
    confidence: float
    method: str


class CustomerInsight(BaseModel):
    total_customers: int
    churn_rate: float
    high_value_customers: int
    top_regions: list[dict[str, str | int | float]]
