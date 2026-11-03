import axios, { AxiosError } from "axios";
import type {
  AgentRun,
  Envelope,
  HealthInfo,
  LlmCheck,
  TicketDetail,
  TicketSummary,
  TraceEvent,
  TriageOutcome,
} from "../types";

const baseURL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api";

export class ApiError extends Error {
  code: string;
  status: number | null;
  details: Record<string, unknown>;

  constructor(message: string, code: string, status: number | null, details = {}) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

const http = axios.create({ baseURL, timeout: 120_000 });

function toApiError(error: unknown): ApiError {
  if (error instanceof ApiError) return error;
  if (error instanceof AxiosError) {
    const body = error.response?.data as Envelope<unknown> | undefined;
    if (body?.error) {
      return new ApiError(body.error.message, body.error.code, error.response?.status ?? null, body.error.details);
    }
    if (error.code === "ECONNABORTED") {
      return new ApiError("The request timed out. The agent may still be running; reload to check.", "timeout", null);
    }
    return new ApiError(
      "Cannot reach the backend. Check that it is running and that VITE_API_BASE_URL is correct.",
      "network_error",
      null,
    );
  }
  return new ApiError("Something went wrong.", "unknown", null);
}

async function unwrap<T>(request: Promise<{ data: Envelope<T> }>): Promise<T> {
  try {
    const { data } = await request;
    if (!data.success || data.data === null) {
      throw new ApiError(data.error?.message ?? "Unexpected response.", data.error?.code ?? "unknown", null);
    }
    return data.data;
  } catch (error) {
    throw toApiError(error);
  }
}

export const api = {
  health: () => unwrap<HealthInfo>(http.get("/health")),
  checkLlm: () => unwrap<LlmCheck>(http.post("/health/llm")),
  listTickets: () => unwrap<TicketSummary[]>(http.get("/tickets")),
  getTicket: (id: string) => unwrap<TicketDetail>(http.get(`/tickets/${encodeURIComponent(id)}`)),
  listTicketRuns: (id: string) => unwrap<AgentRun[]>(http.get(`/tickets/${encodeURIComponent(id)}/runs`)),
  listRuns: () => unwrap<AgentRun[]>(http.get("/agent/runs")),
  getRunTraces: (runId: number) => unwrap<TraceEvent[]>(http.get(`/agent/runs/${runId}/traces`)),
  triage: (id: string) => unwrap<TriageOutcome>(http.post(`/agent/triage/${encodeURIComponent(id)}`)),
};