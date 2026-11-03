import type { AgentRun } from "../../types";
import { cx, formatDateTime } from "../../utils/format";
import { Badge } from "../ui/Badge";
import { Card, CardHeader } from "../ui/Card";

export function RunHistory({
  runs,
  selectedId,
  onSelect,
}: {
  runs: AgentRun[];
  selectedId: number | null;
  onSelect: (id: number) => void;
}) {
  if (runs.length < 2) return null;
  return (
    <Card>
      <CardHeader title="Run history" />
      <ul className="divide-y divide-line">
        {runs.map((run) => (
          <li key={run.id}>
            <button
              type="button"
              onClick={() => onSelect(run.id)}
              aria-pressed={run.id === selectedId}
              className={cx(
                "flex w-full items-center justify-between gap-3 px-5 py-2.5 text-left text-sm hover:bg-subtle",
                run.id === selectedId && "bg-subtle",
              )}
            >
              <span>
                Run #{run.id}
                <span className="ml-2 text-xs text-muted">{formatDateTime(run.started_at)}</span>
              </span>
              <Badge tone={run.status === "completed" ? "success" : run.status === "failed" ? "danger" : "processing"}>
                {run.status === "completed" ? run.resolution_tag : run.status === "failed" ? "Failed" : "Running"}
              </Badge>
            </button>
          </li>
        ))}
      </ul>
    </Card>
  );
}
