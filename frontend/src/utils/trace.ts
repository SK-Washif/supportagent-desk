import type { TraceEvent } from "../types";

export interface ToolStep {
  tool: string;
  parameters: unknown;
  output: unknown;
  error: { code: string; message: string } | null;
  finished: boolean;
}

export interface TraceSummary {
  steps: ToolStep[];
  reasoning: string | null;
  failure: string | null;
}

function asError(value: unknown): { code: string; message: string } | null {
  if (!value || typeof value !== "object") return null;
  const v = value as Record<string, unknown>;
  return {
    code: String(v.code ?? "error"),
    message: String(v.message ?? "The tool call failed."),
  };
}

/**
 * Derives the "Tool called → Parameters → Raw output → Reasoning" view from raw trace events.
 */
export function summarizeTrace(events: TraceEvent[]): TraceSummary {
  const steps: ToolStep[] = [];
  let reasoning: string | null = null;
  let failure: string | null = null;

  const openStep = (tool: string) =>
    [...steps].reverse().find((s) => s.tool === tool && !s.finished);

  for (const event of events) {
    const d = event.details;

    switch (event.event_type) {
      case "TOOL_SELECTED":
        steps.push({
          tool: String(d.tool ?? "(unnamed)"),
          parameters: d.arguments,
          output: null,
          error: null,
          finished: false,
        });
        break;

      case "TOOL_ARGUMENTS_VALIDATED": {
        const step = openStep(String(d.tool ?? ""));
        if (step) {
          step.parameters = d.arguments;
          if (d.error) step.error = asError(d.error);
        }
        break;
      }

      case "TOOL_EXECUTION_COMPLETED": {
        const step = openStep(String(d.tool ?? ""));
        if (step) {
          step.output = d.raw_output ?? d.error ?? null;
          if (d.error) step.error = asError(d.error);
        }
        break;
      }

      case "TOOL_RESULT_RETURNED": {
        const step = openStep(String(d.tool ?? ""));
        if (step) {
          if (!step.output) step.output = d.response;
          step.finished = true;
        }
        break;
      }

      case "FINAL_RESPONSE_GENERATED": {
        // ← NEW: reasoning add kora hoyeche ekhane
        if (d.decision_summary) reasoning = String(d.decision_summary);
        for (const step of steps) {
          if (!step.finished) step.finished = true;
        }
        break;
      }

      case "AGENT_FAILED": {
        const err = asError(d) ?? {
          code: "agent_failed",
          message: "The agent run failed.",
        };
        failure = `[${err.code}] ${err.message}`;
        break;
      }

      default:
        break;
    }
  }

  return { steps, reasoning, failure };
}

export function eventKind(eventType: string): {
  label: string;
  tone: "info" | "success" | "warning" | "danger" | "neutral";
} {
  if (eventType.startsWith("TOOL_EXECUTION_FAILED") || eventType === "AGENT_FAILED") {
    return { label: "Failed", tone: "danger" };
  }
  if (eventType.startsWith("TOOL_")) return { label: "Tool", tone: "info" };
  if (eventType === "FINAL_RESPONSE_GENERATED") return { label: "Reasoning", tone: "success" };
  if (eventType === "AGENT_COMPLETED") return { label: "Done", tone: "success" };
  if (eventType === "AGENT_STARTED") return { label: "Start", tone: "neutral" };
  return { label: "Info", tone: "neutral" };
}