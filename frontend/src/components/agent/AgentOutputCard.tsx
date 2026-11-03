import { Check, Copy } from "lucide-react";
import { useState } from "react";
import type { AgentRun } from "../../types";
import { formatDateTime, formatDuration } from "../../utils/format";
import { Alert } from "../ui/Alert";
import { Button } from "../ui/Button";
import { Card, CardHeader } from "../ui/Card";
import { ResolutionBadge } from "./ResolutionBadge";

async function copyText(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    const area = document.createElement("textarea");
    area.value = text;
    area.style.position = "fixed";
    area.style.opacity = "0";
    document.body.appendChild(area);
    area.select();
    const ok = document.execCommand("copy");
    area.remove();
    return ok;
  }
}

export function AgentOutputCard({ run }: { run: AgentRun }) {
  const [copied, setCopied] = useState(false);

  if (run.status === "failed") {
    return (
      <Card>
        <CardHeader title="Agent result" />
        <div className="space-y-2 p-5">
          <Alert title="The agent run failed">
            {run.error_message ?? "No error details were recorded."}
            {run.error_code && <span className="mt-1 block text-xs text-muted">Code: {run.error_code}</span>}
          </Alert>
          <p className="text-xs text-muted">The ticket was not marked as resolved. Review the trace below, then run again.</p>
        </div>
      </Card>
    );
  }

  if (run.status === "running") {
    return (
      <Card>
        <CardHeader title="Agent result" />
        <div className="p-5">
          <Alert tone="info" title="The agent is still running">
            Results appear here when the run finishes.
          </Alert>
        </div>
      </Card>
    );
  }

  const handleCopy = async () => {
    if (run.customer_response && (await copyText(run.customer_response))) {
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <Card>
      <CardHeader
        title="Agent result"
        action={run.resolution_tag ? <ResolutionBadge tag={run.resolution_tag} /> : undefined}
      />
      <div className="space-y-5 p-5">
        <section>
          <div className="mb-1.5 flex items-center justify-between">
            <h3 className="text-sm font-medium text-ink">Customer Response Draft</h3>
            <Button variant="secondary" className="px-3 py-1.5 text-xs" onClick={handleCopy} icon={copied ? <Check size={14} /> : <Copy size={14} />}>
              {copied ? "Copied" : "Copy response"}
            </Button>
          </div>
          <p className="whitespace-pre-wrap rounded-md border border-line bg-canvas p-3.5 text-sm leading-relaxed">
            {run.customer_response}
          </p>
        </section>
        <section>
          <h3 className="mb-1 text-sm font-medium text-ink">Agent Decision Summary</h3>
          <p className="text-sm text-muted">{run.decision_summary}</p>
        </section>
        <dl className="grid grid-cols-2 gap-x-6 gap-y-2 text-xs text-muted sm:grid-cols-4">
          <div>
            <dt>Tools used</dt>
            <dd className="mt-0.5 text-sm text-ink">{run.tools_used.length ? run.tools_used.join(", ") : "None"}</dd>
          </div>
          <div>
            <dt>Model</dt>
            <dd className="mt-0.5 text-sm text-ink">{run.model_name ?? "—"}</dd>
          </div>
          <div>
            <dt>Completed</dt>
            <dd className="mt-0.5 text-sm text-ink">{formatDateTime(run.completed_at)}</dd>
          </div>
          <div>
            <dt>Duration</dt>
            <dd className="mt-0.5 text-sm text-ink">{formatDuration(run.started_at, run.completed_at)}</dd>
          </div>
        </dl>
      </div>
    </Card>
  );
}
