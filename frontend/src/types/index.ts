export type TicketStatus = "Pending" | "Processing" | "Resolved";
export type RunStatus = "running" | "completed" | "failed";
export type ResolutionTag = "Auto-Resolve" | "Escalate to Sales";

export interface ApiErrorBody {
  code: string;
  message: string;
  details: Record<string, unknown>;
}

export interface Envelope<T> {
  success: boolean;
  data: T | null;
  error: ApiErrorBody | null;
}

export interface Customer {
  customer_id: string;
  name: string;
  email: string;
  current_tier: string;
}

export interface Order {
  order_id: string;
  customer_id: string;
  status: string;
  estimated_delivery: string;
}

export interface TicketSummary {
  ticket_id: string;
  customer_id: string;
  customer_name: string;
  order_id: string | null;
  subject: string;
  status: TicketStatus;
  created_at: string;
  updated_at: string;
}

export interface AgentRun {
  id: number;
  ticket_id: string;
  status: RunStatus;
  resolution_tag: ResolutionTag | null;
  customer_response: string | null;
  decision_summary: string | null;
  tools_used: string[];
  model_name: string | null;
  started_at: string;
  completed_at: string | null;
  error_code: string | null;
  error_message: string | null;
}

export interface TicketDetail extends TicketSummary {
  message: string;
  customer: Customer;
  order: Order | null;
  latest_run: AgentRun | null;
}

export interface TraceEvent {
  id: number;
  agent_run_id: number;
  sequence_number: number;
  event_type: string;
  event_title: string;
  details: Record<string, unknown>;
  status: string;
  created_at: string;
}

export interface TriageOutcome {
  run: AgentRun;
  traces: TraceEvent[];
}

export interface HealthInfo {
  status: string;
  database: string;
  llm_provider: string;
  llm_configured: boolean;
  llm_model: string;
  llm_fallback_model: string | null;
  max_agent_iterations: number;
}

export interface LlmCheck {
  key_valid: boolean;
  models: Record<string, boolean>;
  available_models: string[];
}