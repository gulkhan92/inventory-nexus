import { LucideIcon } from "lucide-react";

type Props = {
  label: string;
  value: string;
  accent: string;
  icon: LucideIcon;
};

export function MetricCard({ label, value, accent, icon: Icon }: Props) {
  return (
    <section className="metric-card">
      <div className="metric-icon" style={{ color: accent }}>
        <Icon size={20} />
      </div>
      <div>
        <p>{label}</p>
        <strong>{value}</strong>
      </div>
    </section>
  );
}
