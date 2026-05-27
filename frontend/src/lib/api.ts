const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

export type DashboardMetrics = {
  total_skus: number;
  inventory_value: number;
  low_stock_count: number;
  reserved_units: number;
  churn_risk_customers: number;
  avg_supplier_reliability: number;
};

export type Product = {
  id: number;
  sku: string;
  name: string;
  description?: string;
  unit_price: number;
  unit_cost: number;
  reorder_point: number;
  reorder_quantity: number;
  quantity_on_hand: number;
  quantity_reserved: number;
  category_name?: string;
  supplier_name?: string;
};

export type ReorderRecommendation = {
  product_id: number;
  sku: string;
  product_name: string;
  current_stock: number;
  reorder_point: number;
  recommended_quantity: number;
  urgency: string;
  rationale: string;
};

export type Forecast = {
  product_id: number;
  sku: string;
  product_name: string;
  expected_30_day_demand: number;
  confidence: number;
  method: string;
};

export type CustomerInsight = {
  total_customers: number;
  churn_rate: number;
  high_value_customers: number;
  top_regions: Array<{ region: string; customers: number; avg_monetary: number }>;
};

export async function login(email: string, password: string): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!response.ok) throw new Error("Unable to sign in");
  const data = await response.json();
  return data.access_token;
}

export async function getJson<T>(path: string, token: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error(`Request failed: ${path}`);
  return response.json() as Promise<T>;
}
