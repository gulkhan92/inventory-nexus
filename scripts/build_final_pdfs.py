from __future__ import annotations

from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "docs" / "generated"
REPORT_PDF = ROOT / "Report.pdf"
FLOW_PDF = ROOT / "Flow.pdf"


def styles():
    base = getSampleStyleSheet()
    base.add(ParagraphStyle(
        name="CoverKicker", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=9,
        textColor=colors.HexColor("#5C6974"), spaceAfter=6, leading=11,
    ))
    base.add(ParagraphStyle(
        name="CoverTitle", parent=base["Title"], fontName="Helvetica-Bold", fontSize=24,
        textColor=colors.black, alignment=TA_LEFT, spaceAfter=8, leading=28,
    ))
    base.add(ParagraphStyle(
        name="CoverSubtitle", parent=base["Normal"], fontName="Helvetica", fontSize=12,
        textColor=colors.HexColor("#5C6974"), leading=16, spaceAfter=18,
    ))
    base.add(ParagraphStyle(
        name="H1Custom", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=15,
        textColor=colors.HexColor("#2E74B5"), leading=18, spaceBefore=14, spaceAfter=7,
    ))
    base.add(ParagraphStyle(
        name="H2Custom", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=12.5,
        textColor=colors.HexColor("#2E74B5"), leading=15, spaceBefore=10, spaceAfter=5,
    ))
    base.add(ParagraphStyle(
        name="H3Custom", parent=base["Heading3"], fontName="Helvetica-Bold", fontSize=11,
        textColor=colors.HexColor("#1F4D78"), leading=13, spaceBefore=8, spaceAfter=4,
    ))
    base.add(ParagraphStyle(
        name="BodyCustom", parent=base["BodyText"], fontName="Helvetica", fontSize=9.8,
        textColor=colors.HexColor("#202A34"), leading=13, spaceAfter=6,
    ))
    base.add(ParagraphStyle(
        name="BulletCustom", parent=base["BodyText"], fontName="Helvetica", fontSize=9.5,
        textColor=colors.HexColor("#202A34"), leading=12.5, leftIndent=12, firstLineIndent=0,
        spaceAfter=3,
    ))
    base.add(ParagraphStyle(
        name="SmallCustom", parent=base["BodyText"], fontName="Helvetica", fontSize=8.4,
        textColor=colors.HexColor("#202A34"), leading=10.5, spaceAfter=2,
    ))
    base.add(ParagraphStyle(
        name="FooterCustom", parent=base["Normal"], fontName="Helvetica", fontSize=8,
        textColor=colors.HexColor("#5C6974"), alignment=TA_CENTER,
    ))
    return base


S = styles()


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#5C6974"))
    canvas.drawCentredString(LETTER[0] / 2, 0.45 * inch, f"Inventory Nexus | Page {doc.page}")
    canvas.restoreState()


def p(text: str):
    return Paragraph(text, S["BodyCustom"])


def h1(text: str):
    return Paragraph(text, S["H1Custom"])


def h2(text: str):
    return Paragraph(text, S["H2Custom"])


def h3(text: str):
    return Paragraph(text, S["H3Custom"])


def bullets(items: list[str]):
    return ListFlowable(
        [ListItem(Paragraph(item, S["BulletCustom"]), leftIndent=14) for item in items],
        bulletType="bullet",
        start="circle",
        leftIndent=16,
        bulletFontName="Helvetica",
        bulletFontSize=7,
        bulletColor=colors.HexColor("#2E74B5"),
    )


def numbers(items: list[str]):
    return ListFlowable(
        [ListItem(Paragraph(item, S["BulletCustom"]), leftIndent=18) for item in items],
        bulletType="1",
        leftIndent=18,
        bulletFontName="Helvetica",
        bulletFontSize=9,
        bulletColor=colors.HexColor("#2E74B5"),
    )


def meta_table(rows: list[tuple[str, str]]):
    table = Table(
        [[Paragraph(f"<b>{a}</b>", S["SmallCustom"]), Paragraph(b, S["SmallCustom"])] for a, b in rows],
        colWidths=[1.25 * inch, 5.4 * inch],
        hAlign="LEFT",
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F2F4F7")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#DADFE6")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
    ]))
    return table


def matrix(headers: list[str], rows: list[list[str]], widths: list[float]):
    data = [[Paragraph(f"<b>{h}</b>", S["SmallCustom"]) for h in headers]]
    data += [[Paragraph(cell, S["SmallCustom"]) for cell in row] for row in rows]
    table = Table(data, colWidths=[w * inch for w in widths], repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F2F4F7")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1F4D78")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#DADFE6")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table


def callout(title: str, text: str):
    table = Table(
        [[Paragraph(f"<b>{title}:</b> {text}", S["BodyCustom"])]],
        colWidths=[6.65 * inch],
        hAlign="LEFT",
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#E8EEF5")),
        ("BOX", (0, 0), (-1, -1), 0.45, colors.HexColor("#B7C7D8")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
    ]))
    return table


def cover(title: str, subtitle: str, audience: str):
    return [
        Paragraph("INVENTORY NEXUS", S["CoverKicker"]),
        Paragraph(title, S["CoverTitle"]),
        Paragraph(subtitle, S["CoverSubtitle"]),
        meta_table([
            ("Audience", audience),
            ("Prepared date", date.today().strftime("%B %d, %Y")),
            ("Status", "Verified local build with backend tests, lint, frontend build, seed import, and live API smoke test"),
        ]),
        Spacer(1, 0.2 * inch),
    ]


def diagram(path: Path):
    return KeepTogether([Image(str(path), width=6.55 * inch, height=2.77 * inch), Spacer(1, 0.08 * inch)])


def build_report():
    story = []
    story += cover(
        "Inventory Nexus Business Report",
        "Production grade inventory management, analytics, and AI planning platform",
        "Business stakeholders, client sponsors, product owners, and delivery leadership",
    )
    story += [
        h1("1. Executive Overview"),
        p("Inventory Nexus is designed as a professional inventory management and decision intelligence platform for modern retail, wholesale, and distribution operations. The application combines operational inventory controls, dashboard reporting, customer intelligence, and AI assisted planning in one coherent system. It is not positioned as a proof of concept. The foundation has been structured so it can be demonstrated to a client today and expanded into a secure production deployment."),
        p("The current implementation includes a React dashboard, a FastAPI backend, a PostgreSQL ready data model, Docker based deployment, seeded product and warehouse data, and an imported customer mart containing 5,878 customer records. The platform supports authenticated access, SKU visibility, stock movement control, low stock monitoring, reorder recommendations, demand planning signals, and customer churn insight."),
        p("The business value is direct: Inventory Nexus gives decision makers a single operating view across inventory health, supplier performance, customer behavior, and replenishment risk. This reduces manual reporting effort, improves planning discipline, and creates a foundation for more advanced forecasting and recommendation use cases."),
        h1("2. Objectives"),
        bullets([
            "Create a client ready inventory management platform with a polished dashboard and reliable backend services.",
            "Support core inventory operations including products, suppliers, warehouses, stock balances, and auditable stock movements.",
            "Use PostgreSQL as the production data store, with Docker Compose for repeatable local and staging deployment.",
            "Integrate the customer mart dataset so business users can see customer segmentation, churn risk, and future recommendation opportunities.",
            "Define a practical AI and ML roadmap that supports demand forecasting, reorder optimization, churn prediction, and next best product recommendations.",
            "Establish a clean architecture that can grow into cloud hosting, stronger security, observability, and enterprise governance.",
        ]),
        PageBreak(),
        h1("3. Technical Architecture"),
        p("The architecture was planned around a simple principle: separate user experience, business logic, and persistence clearly enough that each layer can mature independently. The frontend is responsible for presenting decisions and workflows. The backend owns validation, authentication, data access, domain rules, analytics, and AI planning contracts. The database remains the system of record for operational truth."),
        p("The end to end flow begins when a business user opens the React dashboard and signs in with seeded credentials or future enterprise identity. The dashboard calls FastAPI endpoints using a bearer token. FastAPI routes delegate work to service modules that enforce inventory rules, calculate analytics, read the customer mart, and return structured responses. In production, the same service layer talks to PostgreSQL through SQLAlchemy. In local testing, SQLite is used to make fast automated checks possible."),
        p("This approach gives the project a strong demo experience while keeping a production path visible. The current deterministic AI planning endpoints are deliberately stable contracts. That means the dashboard does not need to change when baseline logic is replaced with trained forecasting, churn, and recommendation models."),
        diagram(GEN / "report_architecture.png"),
        h2("Functional Modules"),
        bullets([
            "Frontend dashboard: React and TypeScript interface for executive metrics, inventory availability, reorder queue, demand forecast, and customer segmentation.",
            "Authentication module: FastAPI login endpoint, password hashing, JWT token creation, and protected route dependencies.",
            "Inventory module: product listing, product creation, warehouse stock balances, and stock movement recording with safeguards against negative inventory.",
            "Analytics module: dashboard metrics for active SKUs, inventory value, low stock alerts, reserved units, churn risk customers, and supplier reliability.",
            "AI planning module: reorder recommendations and baseline thirty day demand forecasts exposed through stable API contracts.",
            "Customer intelligence module: imported customer mart with RFM, churn, order behavior, monetary value, region, and lifespan features.",
            "Data layer: SQLAlchemy ORM models for users, suppliers, warehouses, categories, products, stock items, stock movements, and customer segments.",
            "Deployment layer: Docker Compose stack for PostgreSQL, backend, and frontend services with environment driven configuration.",
        ]),
        h1("4. AI and ML Strategy"),
        p("AI and ML are useful in this project because inventory management is fundamentally a prediction and optimization problem. A production team needs to know what will sell, when stock will run out, which suppliers create fulfillment risk, which customers may churn, and which products should be recommended to increase basket value. Inventory Nexus already exposes the right business surfaces for these capabilities."),
        p("The current application includes deterministic AI planning endpoints for immediate usability. These endpoints produce reorder recommendations from on hand stock, reorder points, supplier lead time, and reorder quantity. They also generate baseline demand forecasts from stock movement history. This is intentionally practical: the client can see the decision workflow now, while the team retains a clear path to replace baseline logic with trained models."),
        matrix(["Capability", "Business Purpose", "Current Status", "Production Direction"], [
            ["Demand forecasting", "Estimate SKU level demand for the next planning window.", "Baseline endpoint available.", "Train models using sales movements, promotions, seasonality, region, and product category."],
            ["Reorder optimization", "Recommend when and how much to reorder.", "Rule based recommendations available.", "Optimize using forecast demand, lead time variability, carrying cost, stockout cost, and supplier reliability."],
            ["Churn prediction", "Identify customers likely to stop purchasing.", "Customer mart includes churn labels and RFM features.", "Train supervised models and explain top churn drivers by segment and region."],
            ["Customer lifetime value", "Prioritize high value customers and retention spend.", "High value customer counts available.", "Build CLV bands and combine them with churn scores for targeted action."],
            ["Next best product", "Increase cross sell and repeat purchase revenue.", "Dataset supports future recommendation work.", "Use behavior, product affinity, category similarity, and embeddings for recommendations."],
        ], [1.35, 1.65, 1.35, 2.3]),
        h1("5. Data Governance and Controls"),
        p("Data governance is important because this platform combines operational inventory data with customer level analytics. The business should treat inventory, supplier, and customer data as controlled assets. The system design already separates domain models and API contracts, which creates a strong place to add access rules, validation, auditing, and retention policies."),
        bullets([
            "Data ownership: Inventory operations owns SKU, warehouse, stock movement, and supplier data. Commercial or CRM teams own customer segmentation inputs.",
            "Data quality: Product SKUs should be unique, stock movement quantities should be validated, and customer import pipelines should reject malformed or duplicate customer IDs.",
            "Auditability: Stock movements are append style operational records, which supports traceability for receipts, sales, returns, transfers, and adjustments.",
            "Privacy: Customer mart data should be handled under privacy rules, with access limited to authorized roles and reporting aggregated wherever possible.",
            "Model governance: Forecasting, churn, and recommendation models should have versioning, validation metrics, monitoring, and human override paths.",
        ]),
        h1("6. Security, Compliance, and Risk View"),
        p("The current implementation includes authenticated API access and password hashing, which is suitable for an early controlled demo. For production, the security model should evolve toward enterprise identity, role based authorization, environment managed secrets, encrypted transport, audit trails, and database level access controls."),
        matrix(["Area", "Current Foundation", "Recommended Next Step"], [
            ["Authentication", "JWT login with hashed password.", "Integrate OAuth or OpenID Connect with enterprise identity provider."],
            ["Authorization", "Protected API routes.", "Add role based permissions for admin, manager, analyst, and viewer access."],
            ["Secrets", "Environment based configuration.", "Move secrets to a cloud secret manager and rotate credentials."],
            ["Database", "PostgreSQL ready schema.", "Enable backups, encryption, migrations, and row level security where needed."],
            ["Monitoring", "Basic local verification.", "Add structured logs, metrics, tracing, uptime alerts, and audit dashboards."],
        ], [1.45, 2.35, 2.85]),
        h1("7. Future Direction"),
        bullets([
            "Cloud deployment on AWS, Azure, or Google Cloud with managed PostgreSQL, container hosting, private networking, and automated deployments.",
            "Database migrations through Alembic, with a formal release process for schema changes.",
            "CI pipeline for tests, linting, build validation, security scans, and Docker image publishing.",
            "Production frontend hosting through a CDN backed static hosting service.",
            "Operational modules for purchase orders, receiving, transfers, cycle counts, returns, stock reservations, and invoice reconciliation.",
            "Advanced ML services with model training jobs, model registry, drift monitoring, and explainability reports.",
            "Enterprise reporting layer for executive KPIs, supplier scorecards, inventory aging, and margin analysis.",
        ]),
        h1("8. Current Verification Status"),
        callout("Verified baseline", "Backend tests pass, backend lint passes, frontend production build passes, the seed script imports the customer mart, and live API endpoints return expected data. This gives the project a reliable baseline for client demonstration and continued development."),
    ]
    SimpleDocTemplate(str(REPORT_PDF), pagesize=LETTER, rightMargin=0.8 * inch, leftMargin=0.8 * inch, topMargin=0.75 * inch, bottomMargin=0.75 * inch).build(story, onFirstPage=footer, onLaterPages=footer)


def build_flow():
    story = []
    story += cover(
        "Inventory Nexus Technical Flow",
        "Technology choices, codebase map, runtime flow, dependency versions, and verification guide",
        "Developers, technical reviewers, solution architects, and maintainers",
    )
    story += [
        h1("1. Purpose of This Guide"),
        p("This guide explains how the Inventory Nexus codebase works from end to end. It is written for a reader who wants to understand the technology choices, folder structure, backend flow, frontend flow, data model, AI service contracts, and testing approach without reading every source file first."),
        p("The project is organized as a full stack application with a React frontend, a FastAPI backend, a PostgreSQL ready persistence layer, and Docker Compose orchestration. The same architecture supports local development, client demonstrations, and a future cloud deployment."),
        h1("2. Repository Layout"),
        matrix(["Path", "Purpose"], [
            ["backend/app/main.py", "Creates the FastAPI app, configures CORS, creates database tables for the baseline, and registers API routes."],
            ["backend/app/api/v1", "HTTP route layer for authentication, inventory, and analytics endpoints."],
            ["backend/app/core", "Configuration and security helpers, including environment settings, password hashing, JWT creation, and token decoding."],
            ["backend/app/db/session.py", "SQLAlchemy engine, declarative base, session factory, and database dependency."],
            ["backend/app/models/domain.py", "SQLAlchemy domain models for users, suppliers, warehouses, categories, products, stock items, stock movements, and customer segments."],
            ["backend/app/schemas/domain.py", "Pydantic request and response models used by API endpoints."],
            ["backend/app/services", "Business logic for inventory, analytics, ML style planning, and seed data import."],
            ["frontend/src/pages/App.tsx", "Main dashboard page. It signs in, loads API data, and renders the operating view."],
            ["frontend/src/lib/api.ts", "Typed frontend API helper functions and TypeScript data shapes."],
            ["docker-compose.yml", "Local container stack for PostgreSQL, backend, and frontend."],
        ], [2.25, 4.4]),
        h1("3. Technology Choices"),
        bullets([
            "React with TypeScript provides a maintainable component model, static typing, and strong ecosystem support for business dashboards.",
            "Vite gives fast local development and a simple production build path.",
            "FastAPI provides automatic OpenAPI documentation, dependency injection, and native Pydantic validation.",
            "SQLAlchemy provides mature ORM mapping, explicit session control, and portability across SQLite testing and PostgreSQL production.",
            "PostgreSQL is the intended production database for transactional reliability, indexing, relational integrity, and future advanced extensions.",
            "Docker Compose creates a repeatable local and staging runtime across frontend, backend, and database services.",
        ]),
        PageBreak(),
        h1("4. End to End Runtime Flow"),
        diagram(GEN / "flow_technical.png"),
        numbers([
            "The user opens the dashboard in the browser. The dashboard signs in with the seeded demo account for local demonstration.",
            "The frontend sends a login request to the FastAPI authentication endpoint and stores the returned bearer token in local storage.",
            "The dashboard requests metrics, products, reorder recommendations, forecasts, and customer insights using the bearer token.",
            "FastAPI validates the token through the shared dependency in backend/app/api/v1/deps.py.",
            "Routers call service functions. The service layer owns business rules, such as preventing stock from becoming negative and calculating low stock recommendations.",
            "The SQLAlchemy session reads and writes records through the models in backend/app/models/domain.py.",
            "The response returns as structured JSON. The React dashboard renders metric cards, tables, alerts, forecasts, and customer summaries.",
        ]),
        h1("5. Backend Flow in Detail"),
        p("The backend starts in backend/app/main.py. When imported, it loads settings, creates database tables for the baseline implementation, configures CORS, and registers the v1 router under /api/v1. The health endpoint remains outside the versioned router so infrastructure can check service availability quickly."),
        p("Route files stay thin. The auth route validates credentials and returns a token. The inventory route lists products, creates products, and records stock movements. The analytics route returns dashboard metrics, reorder recommendations, demand forecasts, and customer insights. This keeps HTTP details separate from business behavior."),
        p("The service layer is where the application becomes more than CRUD. Inventory services aggregate stock quantities, enforce SKU uniqueness, apply movement deltas, stop negative stock, calculate inventory value, and produce reorder recommendations. ML services expose forecast and customer insight contracts. Seed services create demo users, suppliers, warehouses, products, stock, and customer segment records."),
        h1("6. Data Model Summary"),
        matrix(["Entity", "What it Represents", "Important Relationships"], [
            ["User", "Authenticated application user.", "Used by login and token protected routes."],
            ["Supplier", "Vendor that provides products.", "Products reference suppliers; supplier lead time and reliability influence reorder logic."],
            ["Warehouse", "Physical or logical stock location.", "Stock items and stock movements are tied to a warehouse."],
            ["Category", "Product grouping.", "Products belong to categories for reporting and filtering."],
            ["Product", "Sellable or stocked SKU.", "Connected to category, supplier, stock items, and stock movements."],
            ["StockItem", "Current on hand and reserved stock by product and warehouse.", "Aggregated for product availability and low stock checks."],
            ["StockMovement", "Auditable inventory event.", "Records receipts, sales, adjustments, transfers, and returns."],
            ["CustomerSegment", "Imported customer mart record.", "Supports churn, RFM, regional analysis, CLV, and future recommendations."],
        ], [1.35, 2.65, 2.65]),
        h1("7. Frontend Flow in Detail"),
        p("The frontend entry point is frontend/src/main.tsx. It renders App.tsx and loads the shared stylesheet. App.tsx owns the dashboard state, signs in through the API helper, loads five API resources in parallel, and renders the operational dashboard."),
        bullets([
            "MetricCard renders compact KPI tiles for active SKUs, inventory value, low stock alerts, and churn risk.",
            "DataTable renders product availability, category, supplier, stock position, and margin.",
            "The reorder queue renders recommendations from the analytics API and explains why each product needs action.",
            "The forecast panel renders expected thirty day demand and confidence values.",
            "The customer mart panel renders total imported customers, churn rate, high value customers, and top regions.",
        ]),
        h1("8. AI and ML Flow"),
        p("The current AI and ML implementation is intentionally practical. The application exposes stable planning endpoints today and can replace the internal logic with trained models later. This allows frontend, backend, and business stakeholders to agree on workflow before the team invests in heavier model training infrastructure."),
        bullets([
            "Reorder recommendations use current stock, reorder point, reorder quantity, supplier lead time, and urgency classification.",
            "Demand forecast uses stock movement history as a baseline and returns expected thirty day demand, confidence, and method.",
            "Customer insights use the customer mart to calculate total customers, churn rate, high value customers, and leading regions.",
            "Future models can use the same endpoint contracts, which reduces frontend rework and keeps adoption smoother.",
        ]),
        h1("9. Dependency Versions"),
        p("The backend dependency file is fully pinned to reduce testing drift. Important versions are listed below. The complete source of truth is backend/requirements.txt."),
        matrix(["Dependency", "Pinned Version", "Role"], [
            ["fastapi", "0.115.6", "Backend web framework and OpenAPI documentation."],
            ["uvicorn", "0.34.0", "ASGI server for local and container runtime."],
            ["SQLAlchemy", "2.0.50", "ORM and database session layer."],
            ["psycopg and psycopg-binary", "3.2.13", "PostgreSQL driver."],
            ["pydantic", "2.13.4", "Data validation and response schemas."],
            ["pydantic-settings", "2.7.1", "Environment driven configuration."],
            ["python-jose", "3.3.0", "JWT creation and validation."],
            ["passlib", "1.7.4", "Password hashing abstraction."],
            ["bcrypt", "4.0.1", "Password hashing backend compatible with Passlib 1.7.4."],
            ["pytest", "8.3.4", "Backend test runner."],
            ["httpx", "0.28.1", "Test client and smoke test HTTP calls."],
            ["ruff", "0.8.4", "Backend linting."],
        ], [2.1, 1.55, 3.0]),
        p("The frontend top level dependencies are pinned in frontend/package.json and the resolved dependency tree is captured in frontend/package-lock.json. Verified top level versions include React 19.2.6, React DOM 19.2.6, Vite 6.4.2, TypeScript 5.9.3, lucide-react 0.468.0, @vitejs/plugin-react 4.7.0, @types/react 19.2.15, and @types/react-dom 19.2.3."),
        h1("10. Local Commands for Understanding and Verification"),
        bullets([
            "Create or activate the backend environment: cd backend, then source .venv/bin/activate.",
            "Install locked backend dependencies: pip install -r requirements.txt.",
            "Seed local data: python scripts/seed.py.",
            "Run backend tests: pytest -q.",
            "Run backend lint: ruff check app tests scripts.",
            "Start the backend locally: uvicorn app.main:app --host 127.0.0.1 --port 8000.",
            "Install frontend dependencies: cd frontend, then npm install.",
            "Build the frontend: npm run build.",
            "Run the full container stack: docker compose up --build, then docker compose exec backend python scripts/seed.py.",
        ]),
        h1("11. Verification Results"),
        bullets([
            "Backend tests passed with three API tests covering health, authentication, seeded dashboard data, product listing, and reorder recommendations.",
            "Backend lint passed with Ruff across app, tests, and scripts.",
            "Frontend production build passed with Vite and TypeScript.",
            "Seed script successfully created schema and imported the 5,878 row customer mart.",
            "Live API smoke test returned successful responses for health, login, dashboard, products, reorder recommendations, and customer insights.",
        ]),
        h1("12. Technical Improvement Backlog"),
        bullets([
            "Add Alembic migration files instead of relying on create_all during application startup.",
            "Add role based permissions and replace demo login with enterprise identity integration.",
            "Add integration tests against PostgreSQL in Docker for closer production parity.",
            "Add structured logging, request IDs, metrics, and traces.",
            "Add CI workflow for backend tests, frontend builds, linting, dependency review, and Docker image checks.",
            "Add model training jobs, model registry, and monitoring for the AI and ML roadmap.",
        ]),
    ]
    SimpleDocTemplate(str(FLOW_PDF), pagesize=LETTER, rightMargin=0.8 * inch, leftMargin=0.8 * inch, topMargin=0.75 * inch, bottomMargin=0.75 * inch).build(story, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    build_report()
    build_flow()
    print(REPORT_PDF)
    print(FLOW_PDF)
