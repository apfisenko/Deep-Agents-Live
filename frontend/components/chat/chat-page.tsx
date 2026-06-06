"use client";

import { useEffect } from "react";

import { ChatWidget } from "@/components/chat/chat-widget";
import { useChatStream } from "@/lib/hooks/use-chat-stream";

interface ChatPageProps {
  compact?: boolean;
  showTelegramLink?: boolean;
}

export function ChatPage({
  compact = false,
  showTelegramLink = true,
}: ChatPageProps) {
  const { messages, steps, isStreaming, error, sendMessage, ensureSession } =
    useChatStream();

  useEffect(() => {
    ensureSession();
  }, [ensureSession]);

  return (
    <ChatWidget
      messages={messages}
      steps={steps}
      isStreaming={isStreaming}
      error={error}
      onSend={sendMessage}
      compact={compact}
      showTelegramLink={showTelegramLink}
    />
  );
}
