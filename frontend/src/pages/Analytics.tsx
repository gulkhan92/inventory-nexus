import { useEffect, useRef, useState } from "react";
import { BarChart3, ExternalLink, ShieldCheck } from "lucide-react";
import { embedDashboard } from "@superset-ui/embedded-sdk";
import { SupersetGuestToken, getJson, supersetDashboardId, supersetDomain } from "../lib/api";

type Props = {
  token: string | null;
};

export function Analytics({ token }: Props) {
  const mountRef = useRef<HTMLDivElement | null>(null);
  const [status, setStatus] = useState("ready");

  useEffect(() => {
    if (!token || !mountRef.current || !supersetDashboardId) return;
    let disposed = false;

    setStatus("loading");
    embedDashboard({
      id: supersetDashboardId,
      supersetDomain,
      mountPoint: mountRef.current,
      fetchGuestToken: async () => {
        const response = await getJson<SupersetGuestToken>("/superset/guest-token", token);
        return response.token;
      },
      dashboardUiConfig: {
        hideTitle: true,
        filters: { expanded: false },
        urlParams: { standalone: "2" },
      },
    })
      .then(() => {
        if (!disposed) setStatus("embedded");
      })
      .catch(() => {
        if (!disposed) setStatus("error");
      });

    return () => {
      disposed = true;
      if (mountRef.current) mountRef.current.innerHTML = "";
    };
  }, [token]);

  if (!supersetDashboardId) {
    return (
      <section className="analytics-empty">
        <div>
          <BarChart3 size={42} />
          <h2>Apache Superset analytics workspace</h2>
          <p>
            Superset is included in the Docker stack for BI dashboards. Build the dashboard in Superset,
            copy its embedded UUID, then set <b>VITE_SUPERSET_DASHBOARD_ID</b> and <b>SUPERSET_DASHBOARD_ID</b>.
          </p>
          <a href={supersetDomain} target="_blank" rel="noreferrer">
            Open Superset
            <ExternalLink size={16} />
          </a>
        </div>
      </section>
    );
  }

  return (
    <section className="analytics-panel">
      <header className="analytics-header">
        <div>
          <p>Embedded BI</p>
          <h1>Superset dashboard</h1>
        </div>
        <span>
          <ShieldCheck size={16} />
          Guest token secured by backend
        </span>
      </header>
      {status === "error" && (
        <div className="analytics-warning">
          Unable to embed Superset. Check dashboard UUID, allowed domains, and Superset service status.
        </div>
      )}
      {status === "loading" && <div className="analytics-warning">Loading Superset dashboard...</div>}
      <div className="superset-frame" ref={mountRef} />
    </section>
  );
}
