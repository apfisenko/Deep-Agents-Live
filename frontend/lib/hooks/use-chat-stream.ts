"use client";

import { useCallback, useRef, useState } from "react";

import { streamChat } from "@/lib/sse-client";
import { getOrCreateSessionId } from "@/lib/session";
import type { AgentStep, ChatMessage } from "@/lib/types/chat";
import type {
  AgentStepEventData,
  ErrorEventData,
  SseEvent,
} from "@/lib/types/sse";
import { StreamError } from "@/lib/types/sse";

function createMessageId(): string {
  return crypto.randomUUID();
}

function upsertStep(steps: AgentStep[], data: AgentStepEventData): AgentStep[] {
  const index = steps.findIndex((step) => step.id === data.id);
  if (index === -1) {
    return [...steps, { id: data.id, label: data.label, status: data.status }];
  }
  const next = [...steps];
  next[index] = { id: data.id, label: data.label, status: data.status };
  return next;
}

function formatError(error: unknown): string {
  if (error instanceof StreamError) {
    if (typeof error.detail === "string") {
      return error.detail;
    }
    return error.detail.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "Не удалось отправить сообщение";
}

export function useChatStream() {
  const [sessionId, setSessionId] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [steps, setSteps] = useState<AgentStep[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const botMessageIdRef = useRef<string | null>(null);

  const ensureSession = useCallback(() => {
    if (sessionId) {
      return sessionId;
    }
    const id = getOrCreateSessionId();
    setSessionId(id);
    return id;
  }, [sessionId]);

  const handleEvent = useCallback((event: SseEvent) => {
    if (event.type === "agent_step") {
      const data = event.data as AgentStepEventData;
      setSteps((current) => upsertStep(current, data));
      return;
    }

    if (event.type === "token") {
      const text = (event.data as { text: string }).text;
      const botId = botMessageIdRef.current;
      if (!botId) {
        return;
      }
      setMessages((current) =>
        current.map((message) =>
          message.id === botId
            ? { ...message, content: message.content + text }
            : message,
        ),
      );
      return;
    }

    if (event.type === "error") {
      const data = event.data as ErrorEventData;
      setError(data.message);
      setIsStreaming(false);
      return;
    }

    if (event.type === "done") {
      const botId = botMessageIdRef.current;
      if (botId) {
        setMessages((current) =>
          current.map((message) =>
            message.id === botId ? { ...message, isStreaming: false } : message,
          ),
        );
      }
      setIsStreaming(false);
    }
  }, []);

  const sendMessage = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || isStreaming) {
        return;
      }

      abortRef.current?.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      const activeSessionId = ensureSession();
      const userMessage: ChatMessage = {
        id: createMessageId(),
        role: "user",
        content: trimmed,
        createdAt: new Date(),
      };
      const botMessageId = createMessageId();
      botMessageIdRef.current = botMessageId;
      const botMessage: ChatMessage = {
        id: botMessageId,
        role: "bot",
        content: "",
        createdAt: new Date(),
        isStreaming: true,
      };

      setError(null);
      setSteps([]);
      setMessages((current) => [...current, userMessage, botMessage]);
      setIsStreaming(true);

      try {
        await streamChat({
          sessionId: activeSessionId,
          message: trimmed,
          signal: controller.signal,
          onEvent: handleEvent,
        });
      } catch (caught) {
        if (controller.signal.aborted) {
          return;
        }
        const message = formatError(caught);
        setError(message);
        setMessages((current) =>
          current.map((item) =>
            item.id === botMessageId
              ? { ...item, isStreaming: false, content: item.content || message }
              : item,
          ),
        );
      } finally {
        setIsStreaming(false);
        botMessageIdRef.current = null;
      }
    },
    [ensureSession, handleEvent, isStreaming],
  );

  return {
    sessionId,
    messages,
    steps,
    isStreaming,
    error,
    sendMessage,
    ensureSession,
  };
}
