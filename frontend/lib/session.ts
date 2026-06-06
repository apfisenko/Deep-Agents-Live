const SESSION_STORAGE_KEY = "aira_session_id";

function createSessionId(): string {
  return crypto.randomUUID();
}

export function getOrCreateSessionId(): string {
  if (typeof window === "undefined") {
    return "";
  }
  const existing = window.localStorage.getItem(SESSION_STORAGE_KEY);
  if (existing) {
    return existing;
  }
  const sessionId = createSessionId();
  window.localStorage.setItem(SESSION_STORAGE_KEY, sessionId);
  return sessionId;
}
