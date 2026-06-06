const DEFAULT_AGENT_API_URL = "http://localhost:8000";

export function getAgentApiUrl(): string {
  const url = process.env.NEXT_PUBLIC_AGENT_API_URL ?? DEFAULT_AGENT_API_URL;
  return url.replace(/\/$/, "");
}

export function getTelegramBotUrl(): string {
  const username =
    process.env.NEXT_PUBLIC_TELEGRAM_BOT_USERNAME ?? "llmstart_agent_bot";
  return `https://t.me/${username}`;
}
