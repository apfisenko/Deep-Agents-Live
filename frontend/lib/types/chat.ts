import type { AgentStepStatus } from "@/lib/types/sse";

export type MessageRole = "user" | "bot";

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  createdAt: Date;
  isStreaming?: boolean;
}

export interface AgentStep {
  id: string;
  label: string;
  status: AgentStepStatus;
}
