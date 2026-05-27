# Inventory Nexus

Production-oriented inventory management, dashboarding, and AI planning app.

## What is included

- React dashboard for inventory operations, reorder queues, demand forecasts, and customer segmentation.
- FastAPI backend with JWT auth, SQLAlchemy models, product CRUD, stock movement controls, analytics, and ML-ready endpoints.
- PostgreSQL-ready Docker Compose stack.
- Seed importer for the customer mart dataset in `Multi source Customer Mart for Female Recommendati`.

## Quick start

```bash
docker compose up --build
```

In another terminal, seed the backend:

```bash
docker compose exec backend python scripts/seed.py
```

Open:

- Frontend: http://localhost:5173
- API docs: http://localhost:8000/docs

Default seeded login:

- Email: `admin@inventory-nexus.example.com`
- Password: `ChangeMe123!`

## Local backend checks

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

## AI and ML roadmap

The current app includes deterministic AI-planning endpoints so the dashboard works immediately. The intended production roadmap is:

1. Demand forecasting: replace the baseline movement-history method with SKU-level time-series models and promotion/seasonality features.
2. Reorder optimization: combine forecast demand, supplier lead time, reliability, inventory carrying cost, and stockout penalty.
3. Customer intelligence: train churn, CLV, and next-best-offer models from the imported customer mart.
4. Recommendation engine: use customer RFM, product/category affinity, and product embeddings for personalized recommendations.
5. AI assistant: expose safe, schema-aware analytics tools over PostgreSQL and apply role-level access rules before allowing natural language analysis.

## Reference basis

The simple Python inventory examples are useful for domain basics: product records, stock updates, and persistence. This project upgrades those ideas into a web app architecture with Postgres, authenticated APIs, dashboards, analytics, and operational controls.

The Microsoft Zava sample inspired the retail analytics direction: realistic Postgres retail data, product/inventory access, row-level security, and AI-ready search/analytics. The Mendeley customer mart provides an ML-ready gold-layer dataset for churn, segmentation, customer lifetime value, and recommendation features.
