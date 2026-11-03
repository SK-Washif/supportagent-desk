import { useTickets } from "../hooks/useTickets";
import { StatCards } from "../components/dashboard/StatCards";
import { PageHeader } from "../components/layout/AppShell";
import { TicketTable } from "../components/tickets/TicketList";
import { Alert } from "../components/ui/Alert";
import { Button } from "../components/ui/Button";
import { Card, CardHeader } from "../components/ui/Card";
import { Spinner } from "../components/ui/Spinner";

export function OverviewPage() {
  const { tickets, loading, error, refresh } = useTickets();
  return (
    <>
      <PageHeader title="Overview" description="Current state of the support queue." />
      {error ? (
        <div className="space-y-3">
          <Alert title="Could not load tickets">{error.message}</Alert>
          <Button variant="secondary" onClick={() => void refresh()}>
            Try again
          </Button>
        </div>
      ) : loading ? (
        <div className="flex items-center gap-2 py-10 text-sm text-muted">
          <Spinner /> Loading tickets…
        </div>
      ) : (
        <div className="space-y-5">
          <StatCards tickets={tickets} />
          <Card>
            <CardHeader title="Tickets" />
            <TicketTable tickets={tickets} />
          </Card>
        </div>
      )}
    </>
  );
}
