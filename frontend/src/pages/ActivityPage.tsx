import { useEffect, useState } from "react";
import { PageHeader } from "../components/layout/AppShell";
import { ResolutionBadge } from "../components/agent/ResolutionBadge";
import { Alert } from "../components/ui/Alert";
import { Badge } from "../components/ui/Badge";
import { Card } from "../components/ui/Card";
import { EmptyState } from "../components/ui/EmptyState";
import { Spinner } from "../components/ui/Spinner";
import { ticketHref } from "../hooks/useHashRoute";
import { api, type ApiError } from "../services/api";
import type { AgentRun } from "../types";
import { formatDateTime, formatDuration } from "../utils/format";

export function ActivityPage() {
  const [runs, setRuns] = useState<AgentRun[] | null>(null);
  const [error, setError] = useState<ApiError | null>(null);

  useEffect(() => {
    let cancelled = false;
    api
      .listRuns()
      .then((data) => !cancelled && setRuns(data))
      .catch((e) => !cancelled && setError(e as ApiError));
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <>
      <PageHeader title="Agent Activity" description="Every triage run, newest first. Open a ticket to inspect its trace." />
      {error ? (
        <Alert title="Could not load agent activity">{error.message}</Alert>
      ) : runs === null ? (
        <div className="flex items-center gap-2 py-10 text-sm text-muted">
          <Spinner /> Loading activity…
        </div>
      ) : runs.length === 0 ? (
        <Card>
          <EmptyState title="No agent runs yet">Run the AI Triage Agent on a ticket and it will show up here.</EmptyState>
        </Card>
      ) : (
        <Card className="overflow-x-auto">
          <table className="w-full min-w-[720px] text-left text-sm">
            <thead className="border-b border-line text-xs text-muted">
              <tr>
                <th className="px-5 py-2.5 font-medium">Run</th>
                <th className="px-5 py-2.5 font-medium">Ticket</th>
                <th className="px-5 py-2.5 font-medium">Outcome</th>
                <th className="px-5 py-2.5 font-medium">Tools</th>
                <th className="px-5 py-2.5 font-medium">Started</th>
                <th className="px-5 py-2.5 font-medium">Duration</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {runs.map((run) => (
                <tr key={run.id} className="hover:bg-subtle">
                  <td className="px-5 py-3">#{run.id}</td>
                  <td className="px-5 py-3">
                    <a className="font-medium text-primary hover:underline" href={ticketHref(run.ticket_id)}>
                      {run.ticket_id}
                    </a>
                  </td>
                  <td className="px-5 py-3">
                    {run.status === "completed" && run.resolution_tag ? (
                      <ResolutionBadge tag={run.resolution_tag} />
                    ) : (
                      <Badge tone={run.status === "failed" ? "danger" : "processing"}>
                        {run.status === "failed" ? "Failed" : "Running"}
                      </Badge>
                    )}
                  </td>
                  <td className="px-5 py-3 text-muted">{run.tools_used.length ? run.tools_used.join(", ") : "None"}</td>
                  <td className="px-5 py-3 text-muted">{formatDateTime(run.started_at)}</td>
                  <td className="px-5 py-3 text-muted">{formatDuration(run.started_at, run.completed_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
    </>
  );
}
