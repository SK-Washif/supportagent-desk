import { ChevronDown, ChevronRight, Wrench, Brain, CheckCircle2, XCircle } from "lucide-react";
import { useId, useState } from "react";
import type { TraceEvent } from "../../types";
import { cx, formatTime } from "../../utils/format";
import { summarizeTrace, type ToolStep } from "../../utils/trace";
import { Alert } from "../ui/Alert";
import { Badge, type Tone } from "../ui/Badge";
import { Card } from "../ui/Card";
import { EmptyState } from "../ui/EmptyState";
import { Spinner } from "../ui/Spinner";

const statusTone: Record<string, Tone> = {
  success: "success",
  failed: "danger",
  running: "processing",
};

function ToolStepCard({ step }: { step: ToolStep }) {
  const [open, setOpen] = useState(false);
  const panelId = useId();
  return (
    <div className="rounded-lg border border-line bg-surface">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-controls={panelId}
        className="flex w-full items-start justify-between gap-3 rounded-lg px-3.5 py-3 text-left hover:bg-subtle"
      >
        <span className="flex min-w-0 items-start gap-2">
          {open ? (
            <ChevronDown size={15} className="mt-0.5 shrink-0" aria-hidden="true" />
          ) : (
            <ChevronRight size={15} className="mt-0.5 shrink-0" aria-hidden="true" />
          )}
          <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary-soft text-primary">
            <Wrench size={13} aria-hidden="true" />
          </span>
          <span className="min-w-0">
            <span className="block font-mono text-sm font-semibold text-ink">{step.tool}</span>
            <span className="block text-xs text-muted">
              {step.error ? `Failed: ${step.error.code}` : "Tool call"}
            </span>
          </span>
        </span>
        <Badge tone={step.error ? "danger" : step.finished ? "success" : "processing"}>
          {step.error ? "Failed" : step.finished ? "Done" : "Running"}
        </Badge>
      </button>
      {open && (
        <div id={panelId} className="space-y-3 border-t border-line p-3.5">
          <div>
            <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-muted">
              Parameters
            </p>
            <pre className="max-h-40 overflow-auto rounded-md bg-canvas p-2.5 font-mono text-xs text-ink">
              {JSON.stringify(step.parameters, null, 2)}
            </pre>
          </div>
          {step.error ? (
            <div>
              <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-danger">
                Error
              </p>
              <p className="rounded-md border border-danger/30 bg-danger-soft p-2.5 text-xs text-danger">
                <strong>{step.error.code}</strong> — {step.error.message}
              </p>
            </div>
          ) : (
            <div>
              <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-muted">
                Raw output
              </p>
              <pre className="max-h-40 overflow-auto rounded-md bg-canvas p-2.5 font-mono text-xs text-ink">
                {JSON.stringify(step.output, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function TraceItem({ event, last }: { event: TraceEvent; last: boolean }) {
  const [open, setOpen] = useState(false);
  const panelId = useId();
  const failed = event.status === "failed";
  return (
    <li className="relative flex gap-3.5 pb-4 last:pb-0">
      {!last && (
        <span
          aria-hidden="true"
          className="absolute left-[13px] top-7 h-[calc(100%-1.25rem)] w-px bg-line"
        />
      )}
      <span
        className={cx(
          "z-10 flex h-7 w-7 shrink-0 items-center justify-center rounded-full border text-xs font-medium",
          failed
            ? "border-danger/40 bg-danger-soft text-danger"
            : "border-line bg-surface text-muted",
        )}
      >
        {event.sequence_number}
      </span>
      <div className="min-w-0 flex-1">
        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          aria-expanded={open}
          aria-controls={panelId}
          className="flex w-full items-start justify-between gap-3 rounded-md text-left hover:bg-subtle"
        >
          <span className="min-w-0 flex-1 py-0.5">
            <span className="flex items-center gap-1.5 text-sm font-medium text-ink">
              {open ? (
                <ChevronDown size={15} aria-hidden="true" />
              ) : (
                <ChevronRight size={15} aria-hidden="true" />
              )}
              <span className="break-words">{event.event_title}</span>
            </span>
            <span className="ml-[21px] block break-all font-mono text-xs text-muted">
              {event.event_type}
            </span>
          </span>
          <span className="flex shrink-0 flex-col items-end gap-1 py-0.5">
            <Badge tone={statusTone[event.status] ?? "neutral"}>{event.status}</Badge>
            <time dateTime={event.created_at} className="text-xs text-muted">
              {formatTime(event.created_at)}
            </time>
          </span>
        </button>
        {open && (
          <pre
            id={panelId}
            className="mt-2 max-h-80 overflow-auto rounded-md border border-line bg-canvas p-3 font-mono text-xs leading-relaxed text-ink"
          >
            {JSON.stringify(event.details, null, 2)}
          </pre>
        )}
      </div>
    </li>
  );
}

interface Props {
  traces: TraceEvent[];
  loading: boolean;
  error: Error | null;
  hasRun: boolean;
}

export function ExecutionTrace({ traces, loading, error, hasRun }: Props) {
  const [expanded, setExpanded] = useState(true);
  const bodyId = useId();
  const summary = summarizeTrace(traces);

  return (
    <Card>
      <button
        type="button"
        onClick={() => setExpanded((v) => !v)}
        aria-expanded={expanded}
        aria-controls={bodyId}
        className="flex w-full items-center justify-between gap-3 px-5 py-3.5 text-left"
      >
        <h2 className="text-sm font-semibold text-ink">Agent Execution Trace</h2>
        <span className="flex items-center gap-2 text-xs text-muted">
          {hasRun && !loading && `${traces.length} events`}
          {expanded ? (
            <ChevronDown size={16} aria-hidden="true" />
          ) : (
            <ChevronRight size={16} aria-hidden="true" />
          )}
        </span>
      </button>
      {expanded && (
        <div id={bodyId} className="border-t border-line p-5">
          {!hasRun ? (
            <EmptyState title="No trace yet">
              Run the AI Triage Agent to see each step it executes.
            </EmptyState>
          ) : loading ? (
            <div className="flex items-center justify-center gap-2 py-8 text-sm text-muted">
              <Spinner /> Loading trace…
            </div>
          ) : error ? (
            <Alert title="Could not load the trace">{error.message}</Alert>
          ) : traces.length === 0 ? (
            <EmptyState title="This run has no recorded events" />
          ) : (
            <div className="space-y-5">
              {/* ─── Reasoning summary ─────────────────────────────────────── */}
              {summary.reasoning && (
                <div className="rounded-lg border border-success/30 bg-success-soft p-4">
                  <div className="flex items-start gap-2.5">
                    <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-success text-white">
                      <Brain size={13} aria-hidden="true" />
                    </span>
                    <div className="min-w-0">
                      <p className="text-xs font-semibold uppercase tracking-wider text-success">
                        Agent reasoning
                      </p>
                      <p className="mt-1 text-sm leading-relaxed text-ink">
                        {summary.reasoning}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* ─── Failure summary ──────────────────────────────────────── */}
              {summary.failure && (
                <div className="rounded-lg border border-danger/30 bg-danger-soft p-4">
                  <div className="flex items-start gap-2.5">
                    <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-danger text-white">
                      <XCircle size={13} aria-hidden="true" />
                    </span>
                    <div className="min-w-0">
                      <p className="text-xs font-semibold uppercase tracking-wider text-danger">
                        Run failed
                      </p>
                      <p className="mt-1 break-words text-sm text-ink">{summary.failure}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* ─── Tool steps (Tool → Parameters → Output → Reasoning) ──── */}
              {summary.steps.length > 0 && (
                <div>
                  <p className="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-muted">
                    <CheckCircle2 size={13} aria-hidden="true" />
                    Tool invocations ({summary.steps.length})
                  </p>
                  <div className="space-y-2">
                    {summary.steps.map((step, i) => (
                      <ToolStepCard key={`${step.tool}-${i}`} step={step} />
                    ))}
                  </div>
                </div>
              )}

              {/* ─── Raw event timeline ───────────────────────────────────── */}
              <div>
                <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted">
                  Event timeline ({traces.length})
                </p>
                <ol className="pt-1">
                  {traces.map((event, index) => (
                    <TraceItem
                      key={event.id}
                      event={event}
                      last={index === traces.length - 1}
                    />
                  ))}
                </ol>
              </div>
            </div>
          )}
        </div>
      )}
    </Card>
  );
}