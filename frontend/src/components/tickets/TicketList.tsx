import type { TicketStatus, TicketSummary } from "../../types";
import { ticketHref } from "../../hooks/useHashRoute";
import { cx, formatDateTime } from "../../utils/format";
import { EmptyState } from "../ui/EmptyState";
import { StatusBadge } from "./StatusBadge";

interface Props {
  tickets: TicketSummary[];
  selectedId?: string | null;
  /** Locally known live status (e.g. a ticket this browser is triaging right now). */
  statusOverride?: Record<string, TicketStatus>;
}

export function TicketList({ tickets, selectedId = null, statusOverride = {} }: Props) {
  if (tickets.length === 0) {
    return <EmptyState title="No tickets yet">Tickets appear here once the backend has seeded them.</EmptyState>;
  }
  return (
    <ul className="divide-y divide-line">
      {tickets.map((t) => (
        <li key={t.ticket_id}>
          <a
            href={ticketHref(t.ticket_id)}
            aria-current={selectedId === t.ticket_id ? "true" : undefined}
            className={cx(
              "block px-5 py-3.5 transition-colors hover:bg-subtle",
              selectedId === t.ticket_id && "bg-subtle",
            )}
          >
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <p className="truncate text-sm font-medium text-ink">{t.subject}</p>
                <p className="mt-0.5 text-xs text-muted">
                  {t.ticket_id} · {t.customer_id}
                </p>
              </div>
              <StatusBadge status={statusOverride[t.ticket_id] ?? t.status} />
            </div>
            <p className="mt-1.5 text-xs text-muted">Updated {formatDateTime(t.updated_at)}</p>
          </a>
        </li>
      ))}
    </ul>
  );
}

export function TicketTable({ tickets }: { tickets: TicketSummary[] }) {
  if (tickets.length === 0) {
    return <EmptyState title="No tickets yet">Tickets appear here once the backend has seeded them.</EmptyState>;
  }
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[640px] text-left text-sm">
        <thead className="border-b border-line text-xs text-muted">
          <tr>
            <th className="px-5 py-2.5 font-medium">Ticket</th>
            <th className="px-5 py-2.5 font-medium">Customer</th>
            <th className="px-5 py-2.5 font-medium">Subject</th>
            <th className="px-5 py-2.5 font-medium">Status</th>
            <th className="px-5 py-2.5 font-medium">Last updated</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-line">
          {tickets.map((t) => (
            <tr key={t.ticket_id} className="hover:bg-subtle">
              <td className="px-5 py-3 font-medium">
                <a href={ticketHref(t.ticket_id)} className="text-primary hover:underline">
                  {t.ticket_id}
                </a>
              </td>
              <td className="px-5 py-3 text-muted">{t.customer_id}</td>
              <td className="px-5 py-3">{t.subject}</td>
              <td className="px-5 py-3">
                <StatusBadge status={t.status} />
              </td>
              <td className="px-5 py-3 text-muted">{formatDateTime(t.updated_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
