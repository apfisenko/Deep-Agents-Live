/**
 * SSE-транспорт drill-endpoint'а (ядро перенесено из devstand-клиента
 * drill-модуля; формат событий — как у референсного react-shell'а Google):
 * POST JSON ({case} | {version:'v0.9', action, threadId}) ->
 * text/event-stream, каждое событие `data: [{kind:'data'|'error', data|text}]`.
 */
import type { A2uiMessage } from "@a2ui/web_core/v0_9";

interface Part {
  kind: "data" | "text" | "error";
  data?: Record<string, unknown>;
  text?: string;
}

export async function sendA2ui(
  endpoint: string,
  message: unknown,
  onChunk: (messages: A2uiMessage[]) => void
): Promise<void> {
  const body = typeof message === "string" ? message : JSON.stringify(message);
  const response = await fetch(endpoint, { method: "POST", body });
  if (!response.ok && response.status !== 400) {
    throw new Error(`Server error: ${response.status} ${response.statusText}`);
  }

  const reader = response.body?.getReader();
  if (!reader) throw new Error("No response body");
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split(/\r?\n\r?\n/);
    buffer = events.pop() || "";
    for (const event of events) {
      if (!event.startsWith("data: ")) continue;
      const parts = JSON.parse(event.slice(6)) as Part[];
      const msgs: A2uiMessage[] = [];
      for (const part of parts) {
        if (part.kind === "error") {
          await reader.cancel(); // не оставляем соединение висеть
          throw new Error(part.text);
        }
        if (part.kind === "data" && part.data)
          msgs.push(part.data as unknown as A2uiMessage);
      }
      if (msgs.length > 0) onChunk(msgs);
    }
  }
}
