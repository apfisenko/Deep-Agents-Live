import { getAgentApiUrl } from "@/lib/api";
import type { SseEvent, SseEventType } from "@/lib/types/sse";
import { StreamError } from "@/lib/types/sse";

export interface StreamChatOptions {
  sessionId: string;
  message: string;
  signal?: AbortSignal;
  onEvent: (event: SseEvent) => void;
}

interface ParsedSseBlock {
  event?: string;
  data?: string;
}

export function parseSseBlocks(buffer: string): {
  events: SseEvent[];
  remainder: string;
} {
  const normalized = buffer.replace(/\r\n/g, "\n");
  const parts = normalized.split("\n\n");
  const remainder = parts.pop() ?? "";
  const events: SseEvent[] = [];

  for (const part of parts) {
    if (!part.trim()) {
      continue;
    }
    const parsedBlock = blockToEvent(part);
    if (parsedBlock) {
      events.push(parsedBlock);
    }
  }

  const trailing = blockToEvent(remainder.trim());
  if (trailing) {
    events.push(trailing);
    return { events, remainder: "" };
  }

  return { events, remainder };
}

function blockToEvent(part: string): SseEvent | null {
  const block = parseBlock(part);
  if (!block.event || block.data === undefined) {
    return null;
  }
  return parseEvent(block.event, block.data);
}

function parseBlock(part: string): ParsedSseBlock {
  const block: ParsedSseBlock = {};
  for (const line of part.split("\n")) {
    if (line.startsWith("event:")) {
      block.event = line.slice(6).trim();
    } else if (line.startsWith("data:")) {
      const value = line.slice(5).trim();
      block.data = block.data ? `${block.data}\n${value}` : value;
    }
  }
  return block;
}

function parseEvent(type: string, dataJson: string): SseEvent | null {
  try {
    const data = JSON.parse(dataJson) as SseEvent["data"];
    return { type: type as SseEventType, data };
  } catch {
    return null;
  }
}

async function parsePreStreamError(response: Response): Promise<never> {
  let detail: unknown = "Ошибка запроса";
  try {
    const payload = (await response.json()) as { detail?: unknown };
    detail = payload.detail ?? detail;
  } catch {
    detail = await response.text();
  }
  throw new StreamError(response.status, detail as string);
}

export async function streamChat(options: StreamChatOptions): Promise<void> {
  const { sessionId, message, signal, onEvent } = options;
  const response = await fetch(`${getAgentApiUrl()}/api/v1/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      channel: "web",
      message,
    }),
    signal,
  });

  const contentType = response.headers.get("content-type") ?? "";
  if (!response.ok) {
    await parsePreStreamError(response);
  }
  if (!contentType.includes("text/event-stream")) {
    throw new StreamError(
      response.status,
      "Ожидался SSE-стрим, получен другой ответ",
    );
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new StreamError(500, "Пустой ответ сервера");
  }

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }
    buffer += decoder.decode(value, { stream: true });
    const { events, remainder } = parseSseBlocks(buffer);
    buffer = remainder;
    for (const event of events) {
      onEvent(event);
      if (event.type === "error") {
        return;
      }
    }
  }

  if (buffer.trim()) {
    const { events } = parseSseBlocks(`${buffer}\n\n`);
    for (const event of events) {
      onEvent(event);
    }
  }
}
