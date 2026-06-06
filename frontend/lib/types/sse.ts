export type AgentStepStatus = "pending" | "active" | "done";

export interface AgentStepEventData {
  id: string;
  label: string;
  status: AgentStepStatus;
}

export interface ToolCallEventData {
  name: string;
  args: Record<string, unknown>;
  step_id: string;
}

export interface ToolResultEventData {
  name: string;
  result: unknown;
  step_id: string;
}

export interface TokenEventData {
  text: string;
}

export interface DoneEventData {
  session_id: string;
}

export interface ErrorEventData {
  message: string;
  error_class?: string;
  error_code?: string;
}

export type SseEventType =
  | "agent_step"
  | "tool_call"
  | "tool_result"
  | "token"
  | "done"
  | "error";

export interface SseEvent {
  type: SseEventType;
  data:
    | AgentStepEventData
    | ToolCallEventData
    | ToolResultEventData
    | TokenEventData
    | DoneEventData
    | ErrorEventData;
}

export interface ProviderErrorDetail {
  message: string;
  error_class?: string;
  error_code?: string;
  retryable?: boolean;
}

export class StreamError extends Error {
  readonly status: number;
  readonly detail: ProviderErrorDetail | string;

  constructor(status: number, detail: ProviderErrorDetail | string) {
    const message =
      typeof detail === "string" ? detail : detail.message ?? "Ошибка запроса";
    super(message);
    this.name = "StreamError";
    this.status = status;
    this.detail = detail;
  }
}
