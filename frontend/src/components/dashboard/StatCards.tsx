import type { TicketSummary } from "../../types";
import { Card } from "../ui/Card";

export function StatCards({ tickets }: { tickets: TicketSummary[] }) {
  const count = (status: string) => tickets.filter((t) => t.status === status).length;
  const stats = [
    { label: "Total Tickets", value: tickets.length, color: "text-ink" },
    { label: "Pending", value: count("Pending"), color: "text-warning" },
    { label: "Processing", value: count("Processing"), color: "text-processing" },
    { label: "Resolved", value: count("Resolved"), color: "text-success" },
  ];
  return (
    <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
      {stats.map((s) => (
        <Card key={s.label} className="px-5 py-4">
          <p className="text-sm text-muted">{s.label}</p>
          <p className={`mt-1 text-2xl font-semibold ${s.color}`}>{s.value}</p>
        </Card>
      ))}
    </div>
  );
}
