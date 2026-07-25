/**
 * Promptfoo target for Agent Core POST /api/v1/chat.
 * Generates a fresh session_id per call (isolation — no shared dialog state).
 */
import { randomUUID } from "node:crypto";

const DEFAULT_URL = "http://127.0.0.1:8000/api/v1/chat";
const DEFAULT_TIMEOUT_MS = 120_000;

/** Promptfoo may pass unresolved {{env.*}} literals to file providers. */
function resolveConfiguredUrl(raw) {
  const value = String(raw ?? "").trim();
  if (!value || value.includes("{{")) {
    return "";
  }
  return value;
}

export default class AgentChatTarget {
  constructor(options) {
    this.config = options?.config ?? {};
    const fromConfig = resolveConfiguredUrl(this.config.url);
    const fromEnv = String(process.env.AGENT_CHAT_URL ?? "").trim();
    this.url = fromConfig || fromEnv || DEFAULT_URL;
    this.timeoutMs = Number(this.config.timeoutMs ?? DEFAULT_TIMEOUT_MS);
  }

  id() {
    return "agent-chat-http";
  }

  async callApi(prompt) {
    const message = String(prompt ?? "").trim();
    if (!message) {
      return { error: "Empty prompt/message" };
    }

    const body = {
      session_id: randomUUID(),
      channel: "telegram",
      message,
    };

    let response;
    try {
      response = await fetch(this.url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
        signal: AbortSignal.timeout(this.timeoutMs),
      });
    } catch (err) {
      return { error: `Request failed: ${err?.message ?? err}` };
    }

    const text = await response.text();
    let data;
    try {
      data = text ? JSON.parse(text) : {};
    } catch {
      return {
        error: `Non-JSON response ${response.status}: ${text.slice(0, 400)}`,
      };
    }

    if (!response.ok) {
      return {
        error: `HTTP ${response.status}: ${text.slice(0, 400)}`,
        raw: data,
      };
    }

    const output = typeof data.reply === "string" ? data.reply : "";
    if (!output.trim()) {
      return { error: "ChatResponse.reply missing or empty", raw: data };
    }

    return {
      output,
      metadata: {
        session_id: data.session_id,
        blockMarkerPresent: output.includes("SECURITY_BLOCKED"),
      },
    };
  }
}
