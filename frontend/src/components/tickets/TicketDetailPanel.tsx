import { Bot } from "lucide-react";
import { useTicketWorkspace } from "../../hooks/useTicketWorkspace";
import { formatDateTime } from "../../utils/format";
import { AgentOutputCard } from "../agent/AgentOutputCard";
import { RunHistory } from "../agent/RunHistory";
import { ExecutionTrace } from "../traces/ExecutionTrace";
import { Alert } from "../ui/Alert";
import { Button } from "../ui/Button";
import { Card, CardHeader } from "../ui/Card";
import { Spinner } from "../ui/Spinner";
import { StatusBadge } from "./StatusBadge";

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <dt className="text-xs text-muted">{label}</dt>
      <dd className="mt-0.5 text-sm text-ink">{children}</dd>
    </div>
  );
}

interface Props {
  ticketId: string;
  onChanged: () => void;
  onLiveStatus: (ticketId: string, processing: boolean) => void;
}

export function TicketDetailPanel({ ticketId, onChanged, onLiveStatus }: Props) {
  const w = useTicketWorkspace(ticketId, onChanged);

  if (w.loading) {
    return (
      <Card className="flex items-center justify-center gap-2 py-16 text-sm text-muted">
        <Spinner /> Loading ticket…
      </Card>
    );
  }
  if (w.loadError || !w.ticket) {
    return (
      <Alert title={w.loadError?.code === "not_found" ? "Ticket not found" : "Could not load this ticket"}>
        {w.loadError?.message}
      </Alert>
    );
  }

  const { ticket } = w;
  const busy = w.triaging || ticket.status === "Processing";
  const displayStatus = w.triaging ? "Processing" : ticket.status;

  const handleRun = () => {
    onLiveStatus(ticket.ticket_id, true);
    void w.triage().finally(() => onLiveStatus(ticket.ticket_id, false));
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader title={`${ticket.ticket_id} · ${ticket.subject}`} action={<StatusBadge status={displayStatus} />} />
        <div className="space-y-5 p-5">
          <dl className="grid grid-cols-2 gap-x-6 gap-y-3 sm:grid-cols-3">
            <Field label="Customer">
              {ticket.customer.name}
              <span className="block text-xs text-muted">{ticket.customer.customer_id}</span>
            </Field>
            <Field label="Email">
              <span className="break-all">{ticket.customer.email}</span>
            </Field>
            <Field label="Account tier">{ticket.customer.current_tier}</Field>
            <Field label="Order">
              {ticket.order ? (
                <>
                  {ticket.order.order_id}
                  <span className="block text-xs text-muted">{ticket.order.status}</span>
                </>
              ) : (
                <span className="text-muted">No order on this ticket</span>
              )}
            </Field>
            <Field label="Created">{formatDateTime(ticket.created_at)}</Field>
            <Field label="Last updated">{formatDateTime(ticket.updated_at)}</Field>
          </dl>
          <section>
            <h3 className="mb-1.5 text-sm font-medium text-ink">Customer message</h3>
            <p className="whitespace-pre-wrap rounded-md border border-line bg-canvas p-3.5 text-sm leading-relaxed">
              {ticket.message}
            </p>
          </section>
          <div className="flex flex-wrap items-center gap-3">
            <Button onClick={handleRun} disabled={busy} loading={w.triaging} icon={<Bot size={16} />} className="px-5 py-2.5">
              {w.triaging ? "Processing..." : "Run AI Triage Agent"}
            </Button>
            {busy && !w.triaging && (
              <span className="text-xs text-muted">Another run is in progress for this ticket.</span>
            )}
          </div>
        </div>
      </Card>

      {w.triageError && (
        <Alert title={w.triageError.code === "conflict" ? "Already processing" : "Triage did not complete"}>
          {w.triageError.message}
        </Alert>
      )}

      {w.selectedRun ? (
        <AgentOutputCard run={w.selectedRun} />
      ) : (
        !w.triaging && (
          <Card>
            <CardHeader title="Agent result" />
            <div className="px-6 py-8 text-center text-sm text-muted">
              No agent result yet. Run the AI Triage Agent to draft a customer response.
            </div>
          </Card>
        )
      )}

      <RunHistory runs={w.runs} selectedId={w.selectedRun?.id ?? null} onSelect={w.selectRun} />
      <ExecutionTrace traces={w.traces} loading={w.tracesLoading} error={w.tracesError} hasRun={w.selectedRun !== null} />
    </div>
  );
}
