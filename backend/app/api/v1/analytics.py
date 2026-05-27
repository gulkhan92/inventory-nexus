from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select

from app.api.v1.deps import DbSession, get_current_user
from app.models.domain import CustomerSegment, User
from app.schemas.domain import CustomerInsight, DashboardMetrics, DemandForecast, ReorderRecommendation
from app.services.inventory import dashboard_metrics, low_stock_recommendations
from app.services.ml import customer_insights, demand_forecast

router = APIRouter(prefix="/analytics", tags=["analytics"])
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("/dashboard", response_model=DashboardMetrics)
def dashboard(db: DbSession, _: CurrentUser) -> DashboardMetrics:
    metrics = dashboard_metrics(db)
    metrics["churn_risk_customers"] = db.scalar(
        select(func.count(CustomerSegment.id)).where(CustomerSegment.churn_label == 1)
    ) or 0
    return DashboardMetrics(**metrics)


@router.get("/reorder-recommendations", response_model=list[ReorderRecommendation])
def reorder_recommendations(db: DbSession, _: CurrentUser) -> list[ReorderRecommendation]:
    return [ReorderRecommendation(**item) for item in low_stock_recommendations(db)]


@router.get("/demand-forecast", response_model=list[DemandForecast])
def forecast(db: DbSession, _: CurrentUser) -> list[DemandForecast]:
    return [DemandForecast(**item) for item in demand_forecast(db)]


@router.get("/customers", response_model=CustomerInsight)
def customers(db: DbSession, _: CurrentUser) -> CustomerInsight:
    return CustomerInsight(**customer_insights(db))
