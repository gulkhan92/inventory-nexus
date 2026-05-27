import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, Boxes, BrainCircuit, CircleDollarSign, PackageCheck, Search, ShieldCheck, Users } from "lucide-react";
import {
  CustomerInsight,
  DashboardMetrics,
  Forecast,
  Product,
  ReorderRecommendation,
  getJson,
  login,
} from "../lib/api";
import { DataTable } from "../components/DataTable";
import { MetricCard } from "../components/MetricCard";

const formatter = new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 });
const currency = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });

export function App() {
  const [token, setToken] = useState<string | null>(localStorage.getItem("inventory-token"));
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [recommendations, setRecommendations] = useState<ReorderRecommendation[]>([]);
  const [forecasts, setForecasts] = useState<Forecast[]>([]);
  const [customers, setCustomers] = useState<CustomerInsight | null>(null);
  const [query, setQuery] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      login("admin@inventory-nexus.example.com", "ChangeMe123!")
        .then((value) => {
          localStorage.setItem("inventory-token", value);
          setToken(value);
        })
        .catch(() => setError("Seed the backend, then refresh the dashboard."));
    }
  }, [token]);

  useEffect(() => {
    if (!token) return;
    Promise.all([
      getJson<DashboardMetrics>("/analytics/dashboard", token),
      getJson<Product[]>("/inventory/products", token),
      getJson<ReorderRecommendation[]>("/analytics/reorder-recommendations", token),
      getJson<Forecast[]>("/analytics/demand-forecast", token),
      getJson<CustomerInsight>("/analytics/customers", token),
    ])
      .then(([dashboard, productList, reorderList, forecastList, customerInsight]) => {
        setMetrics(dashboard);
        setProducts(productList);
        setRecommendations(reorderList);
        setForecasts(forecastList);
        setCustomers(customerInsight);
      })
      .catch(() => setError("Unable to load dashboard data."));
  }, [token]);

  const filteredProducts = useMemo(() => {
    const lower = query.toLowerCase();
    return products.filter((product) => `${product.sku} ${product.name}`.toLowerCase().includes(lower));
  }, [products, query]);

  if (error) {
    return <main className="status-screen">{error}</main>;
  }

  if (!metrics || !customers) {
    return <main className="status-screen">Loading Inventory Nexus...</main>;
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <PackageCheck size={26} />
          <span>Inventory Nexus</span>
        </div>
        <nav>
          <a className="active">Operations</a>
          <a>Inventory</a>
          <a>Suppliers</a>
          <a>Customers</a>
          <a>AI planning</a>
        </nav>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <p>Unified inventory command center</p>
            <h1>Stock, demand, and customer intelligence</h1>
          </div>
          <div className="search-box">
            <Search size={18} />
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search SKU or product" />
          </div>
        </header>

        <section className="metrics-grid">
          <MetricCard label="Active SKUs" value={formatter.format(metrics.total_skus)} accent="#0f766e" icon={Boxes} />
          <MetricCard label="Inventory value" value={currency.format(metrics.inventory_value)} accent="#b45309" icon={CircleDollarSign} />
          <MetricCard label="Low stock alerts" value={formatter.format(metrics.low_stock_count)} accent="#dc2626" icon={AlertTriangle} />
          <MetricCard label="Churn risk" value={formatter.format(metrics.churn_risk_customers)} accent="#7c3aed" icon={Users} />
        </section>

        <section className="content-grid">
          <section className="panel wide">
            <div className="panel-heading">
              <div>
                <p>Inventory</p>
                <h2>Product availability</h2>
              </div>
              <span className="quality-badge">
                <ShieldCheck size={16} />
                {Math.round(metrics.avg_supplier_reliability * 100)}% supplier reliability
              </span>
            </div>
            <DataTable products={filteredProducts} />
          </section>

          <section className="panel">
            <div className="panel-heading">
              <div>
                <p>AI planning</p>
                <h2>Reorder queue</h2>
              </div>
              <BrainCircuit size={22} />
            </div>
            <div className="stack">
              {recommendations.map((item) => (
                <article className="alert-row" key={item.product_id}>
                  <strong>{item.product_name}</strong>
                  <span>{item.rationale}</span>
                  <b>Order {item.recommended_quantity}</b>
                </article>
              ))}
            </div>
          </section>

          <section className="panel">
            <div className="panel-heading">
              <div>
                <p>Forecast</p>
                <h2>30 day demand</h2>
              </div>
            </div>
            <div className="stack compact">
              {forecasts.slice(0, 5).map((forecast) => (
                <article className="forecast-row" key={forecast.product_id}>
                  <span>{forecast.product_name}</span>
                  <strong>{forecast.expected_30_day_demand} units</strong>
                  <progress value={forecast.confidence} max="1" />
                </article>
              ))}
            </div>
          </section>

          <section className="panel">
            <div className="panel-heading">
              <div>
                <p>Customer mart</p>
                <h2>Segmentation signal</h2>
              </div>
            </div>
            <div className="customer-summary">
              <strong>{formatter.format(customers.total_customers)}</strong>
              <span>customers imported</span>
              <b>{(customers.churn_rate * 100).toFixed(1)}% churn rate</b>
            </div>
            <div className="region-list">
              {customers.top_regions.map((region) => (
                <span key={region.region}>
                  {region.region} <b>{region.customers}</b>
                </span>
              ))}
            </div>
          </section>
        </section>
      </section>
    </main>
  );
}
