import { ArrowLeft } from "lucide-react";
import { useCallback, useState } from "react";
import { PageHeader } from "../components/layout/AppShell";
import { TicketDetailPanel } from "../components/tickets/TicketDetailPanel";
import { TicketList } from "../components/tickets/TicketList";
import { Alert } from "../components/ui/Alert";
import { Button } from "../components/ui/Button";
import { Card, CardHeader } from "../components/ui/Card";
import { Spinner } from "../components/ui/Spinner";
import { useTickets } from "../hooks/useTickets";
import type { TicketStatus } from "../types";
import { cx } from "../utils/format";

export function TicketsPage({ ticketId }: { ticketId: string | null }) {
  const { tickets, loading, error, refresh } = useTickets();
  const [live, setLive] = useState<Record<string, TicketStatus>>({});

  const onLiveStatus = useCallback((id: string, processing: boolean) => {
    setLive((prev) => {
      const next = { ...prev };
      if (processing) next[id] = "Processing";
      else delete next[id];
      return next;
    });
  }, []);

  return (
    <>
      <PageHeader title="All Tickets" description="Select a ticket to review it and run the triage agent." />
      {error ? (
        <div className="space-y-3">
          <Alert title="Could not load tickets">{error.message}</Alert>
          <Button variant="secondary" onClick={() => void refresh()}>
            Try again
          </Button>
        </div>
      ) : (
        <div className="grid gap-5 lg:grid-cols-[340px_minmax(0,1fr)]">
          <Card className={cx("h-fit", ticketId && "hidden lg:block")}>
            <CardHeader title="Tickets" />
            {loading ? (
              <div className="flex items-center justify-center gap-2 py-10 text-sm text-muted">
                <Spinner /> Loading tickets…
              </div>
            ) : (
              <TicketList tickets={tickets} selectedId={ticketId} statusOverride={live} />
            )}
          </Card>
          <div className="min-w-0">
            {ticketId ? (
              <>
                <a href="#/tickets" className="mb-3 inline-flex items-center gap-1.5 text-sm text-muted hover:text-ink lg:hidden">
                  <ArrowLeft size={15} aria-hidden="true" /> Back to tickets
                </a>
                <TicketDetailPanel
                  key={ticketId}
                  ticketId={ticketId}
                  onChanged={() => void refresh()}
                  onLiveStatus={onLiveStatus}
                />
              </>
            ) : (
              <Card className="hidden px-6 py-16 text-center text-sm text-muted lg:block">
                Select a ticket from the list to see its details.
              </Card>
            )}
          </div>
        </div>
      )}
    </>
  );
}
