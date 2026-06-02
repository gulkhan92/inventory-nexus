from sqlalchemy import text
from sqlalchemy.orm import Session


def ensure_reporting_views(db: Session) -> None:
    dialect_name = db.bind.dialect.name if db.bind is not None else ""
    if dialect_name != "postgresql":
        return

    statements = [
        "CREATE SCHEMA IF NOT EXISTS analytics",
        """
        CREATE OR REPLACE VIEW analytics.inventory_snapshot_v AS
        SELECT
            p.id AS product_id,
            p.sku,
            p.name AS product_name,
            c.name AS category_name,
            s.name AS supplier_name,
            s.lead_time_days,
            s.reliability_score,
            w.code AS warehouse_code,
            w.name AS warehouse_name,
            w.city AS warehouse_city,
            w.country AS warehouse_country,
            si.quantity_on_hand,
            si.quantity_reserved,
            GREATEST(si.quantity_on_hand - si.quantity_reserved, 0) AS available_quantity,
            p.reorder_point,
            p.reorder_quantity,
            p.unit_cost,
            p.unit_price,
            ROUND((si.quantity_on_hand * p.unit_cost)::numeric, 2) AS inventory_value,
            ROUND(((p.unit_price - p.unit_cost) / NULLIF(p.unit_price, 0))::numeric, 4) AS gross_margin_rate,
            CASE
                WHEN si.quantity_on_hand <= GREATEST(5, p.reorder_point / 2) THEN 'critical'
                WHEN si.quantity_on_hand <= p.reorder_point THEN 'watch'
                ELSE 'healthy'
            END AS stock_status,
            si.updated_at
        FROM stock_items si
        JOIN products p ON p.id = si.product_id
        JOIN categories c ON c.id = p.category_id
        JOIN suppliers s ON s.id = p.supplier_id
        JOIN warehouses w ON w.id = si.warehouse_id
        """,
        """
        CREATE OR REPLACE VIEW analytics.reorder_queue_v AS
        SELECT
            product_id,
            sku,
            product_name,
            category_name,
            supplier_name,
            lead_time_days,
            reliability_score,
            warehouse_code,
            quantity_on_hand AS current_stock,
            reorder_point,
            reorder_quantity AS recommended_quantity,
            stock_status AS urgency,
            inventory_value,
            CASE
                WHEN stock_status = 'critical'
                THEN 'Stock is materially below the reorder point and needs immediate purchasing review.'
                WHEN stock_status = 'watch'
                THEN 'Stock is below reorder point and should be reviewed in the next planning cycle.'
                ELSE 'Stock is above reorder threshold.'
            END AS recommendation_reason
        FROM analytics.inventory_snapshot_v
        WHERE stock_status IN ('critical', 'watch')
        """,
        """
        CREATE OR REPLACE VIEW analytics.stock_movements_v AS
        SELECT
            sm.id AS movement_id,
            sm.occurred_at,
            sm.movement_type,
            sm.quantity,
            sm.reference,
            sm.note,
            p.id AS product_id,
            p.sku,
            p.name AS product_name,
            c.name AS category_name,
            s.name AS supplier_name,
            w.code AS warehouse_code,
            w.name AS warehouse_name,
            CASE
                WHEN sm.movement_type IN ('receipt', 'return_in') THEN sm.quantity
                WHEN sm.movement_type = 'adjustment' THEN sm.quantity
                ELSE -sm.quantity
            END AS signed_quantity
        FROM stock_movements sm
        JOIN products p ON p.id = sm.product_id
        JOIN categories c ON c.id = p.category_id
        JOIN suppliers s ON s.id = p.supplier_id
        JOIN warehouses w ON w.id = sm.warehouse_id
        """,
        """
        CREATE OR REPLACE VIEW analytics.supplier_scorecard_v AS
        SELECT
            s.id AS supplier_id,
            s.name AS supplier_name,
            s.lead_time_days,
            s.reliability_score,
            COUNT(DISTINCT p.id) AS sku_count,
            COALESCE(SUM(si.quantity_on_hand), 0) AS total_on_hand,
            ROUND(COALESCE(SUM(si.quantity_on_hand * p.unit_cost), 0)::numeric, 2) AS inventory_value,
            COUNT(DISTINCT CASE WHEN si.quantity_on_hand <= p.reorder_point THEN p.id END) AS low_stock_skus
        FROM suppliers s
        LEFT JOIN products p ON p.supplier_id = s.id
        LEFT JOIN stock_items si ON si.product_id = p.id
        GROUP BY s.id, s.name, s.lead_time_days, s.reliability_score
        """,
        """
        CREATE OR REPLACE VIEW analytics.customer_segments_v AS
        SELECT
            id,
            external_customer_id,
            country,
            region,
            recency,
            frequency,
            monetary,
            avg_order_value,
            churn_label,
            total_items,
            unique_products,
            total_orders,
            customer_lifespan_days,
            CASE
                WHEN monetary >= 1000 THEN 'high_value'
                WHEN monetary >= 250 THEN 'mid_value'
                ELSE 'emerging'
            END AS value_segment,
            CASE
                WHEN churn_label = 1 THEN 'at_risk'
                ELSE 'active'
            END AS churn_status
        FROM customer_segments
        """,
        """
        CREATE OR REPLACE VIEW analytics.customer_region_summary_v AS
        SELECT
            region,
            country,
            COUNT(*) AS customer_count,
            ROUND(AVG(monetary)::numeric, 2) AS avg_monetary,
            ROUND(SUM(monetary)::numeric, 2) AS total_monetary,
            ROUND(AVG(avg_order_value)::numeric, 2) AS avg_order_value,
            ROUND(AVG(churn_label)::numeric, 4) AS churn_rate,
            COUNT(*) FILTER (WHERE monetary >= 1000) AS high_value_customers
        FROM customer_segments
        GROUP BY region, country
        """,
    ]

    for statement in statements:
        db.execute(text(statement))

    db.execute(text("GRANT USAGE ON SCHEMA analytics TO inventory"))
    db.execute(text("GRANT SELECT ON ALL TABLES IN SCHEMA analytics TO inventory"))
