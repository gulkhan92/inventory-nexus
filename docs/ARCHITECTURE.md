# Inventory Nexus Architecture

## System shape

Inventory Nexus is a monorepo with three deployable layers:

- `frontend`: React and TypeScript dashboard for operators, managers, and executives.
- `backend`: FastAPI service with REST APIs, domain logic, auth, analytics, and ML endpoints.
- `postgres`: system of record for inventory, suppliers, stock movements, and customer intelligence.
- `superset`: Apache Superset BI layer for dashboards and embedded analytics.

## Core domain model

- Product: SKU, category, supplier, price, cost, reorder policy.
- Warehouse: physical stock location.
- Stock item: on-hand and reserved inventory by product and warehouse.
- Stock movement: auditable receipt, sale, transfer, return, and adjustment events.
- Supplier: lead time and reliability inputs for reorder planning.
- Customer segment: imported customer mart features for churn and recommendation models.

## Production-grade priorities

- Authenticated API surface with scoped routes.
- Append-only stock movements for auditability.
- Postgres-first deployment with Docker Compose.
- Explicit seed/import path for reproducible demos.
- API tests for health, auth, dashboard, products, and reorder recommendations.
- ML endpoints kept behind stable contracts so the baseline can be replaced with trained models without breaking the UI.

## Data and AI plan

The local customer mart has 17 engineered features per customer: RFM, monetary value, order behavior, churn labels, item diversity, geography, and lifespan. In production, this supports:

- Churn risk scoring.
- Customer lifetime value bands.
- Demand planning by region and customer segment.
- Next-best-product recommendations.
- Executive customer health dashboards.

The Zava reference pattern is useful for the next phase: PostgreSQL row-level security, pgvector product embeddings, semantic product search, and AI assistant access through narrowly scoped tools instead of unrestricted SQL.

## Superset integration

Apache Superset is used as the business intelligence layer, not as a replacement for the React operational dashboard. The React app remains the product surface for inventory workflows, while Superset provides analyst friendly charting, dashboarding, exploration, and future embedded BI.

Superset uses a separate PostgreSQL metadata database for charts, dashboards, users, permissions, and logs. The Inventory Nexus application database remains the data source. Superset should connect through curated datasets in the `analytics` schema rather than raw operational tables.

Recommended Superset datasets:

- `analytics.inventory_snapshot_v`
- `analytics.reorder_queue_v`
- `analytics.stock_movements_v`
- `analytics.supplier_scorecard_v`
- `analytics.customer_segments_v`
- `analytics.customer_region_summary_v`

The frontend includes an Analytics view that can embed a Superset dashboard with `@superset-ui/embedded-sdk`. FastAPI exposes `/api/v1/superset/guest-token`, which authenticates to Superset server side and returns a guest token for the configured dashboard UUID.
