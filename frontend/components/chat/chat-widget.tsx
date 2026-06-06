"use client";

import { ScrollArea } from "@/components/ui/scroll-area";
import { getTelegramBotUrl } from "@/lib/api";
import type { AgentStep, ChatMessage } from "@/lib/types/chat";

import { ChatHeader } from "@/components/chat/chat-header";
import { ChatInput } from "@/components/chat/chat-input";
import { ChatShell } from "@/components/chat/chat-shell";
import { MessageBubble } from "@/components/chat/message-bubble";
import { QuickChips } from "@/components/chat/quick-chips";
import { ThinkingPanel } from "@/components/chat/thinking-panel";

interface ChatWidgetProps {
  messages: ChatMessage[];
  steps: AgentStep[];
  isStreaming: boolean;
  error: string | null;
  onSend: (message: string) => void;
  compact?: boolean;
  showTelegramLink?: boolean;
}

export function ChatWidget({
  messages,
  steps,
  isStreaming,
  error,
  onSend,
  compact = false,
  showTelegramLink = true,
}: ChatWidgetProps) {
  return (
    <ChatShell compact={compact} className="max-w-md">
      <ChatHeader showClose={compact} />
      <ScrollArea className="min-h-0 flex-1 px-4 py-4">
        <div className="space-y-3">
          {messages.length === 0 ? (
            <p className="text-center text-sm text-slate-600">
              Привет! Я Айра — помогу выбрать курс на llmstart.ru
            </p>
          ) : null}
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
        </div>
      </ScrollArea>
      <ThinkingPanel steps={steps} isStreaming={isStreaming} />
      {error ? (
        <p className="px-4 pb-2 text-sm text-red-600" role="alert">
          {error}
        </p>
      ) : null}
      <QuickChips onSelect={onSend} disabled={isStreaming} />
      <ChatInput onSend={onSend} disabled={isStreaming} />
      {showTelegramLink ? (
        <div className="border-t border-white/20 px-4 py-2 text-center">
          <a
            href={getTelegramBotUrl()}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs font-medium text-sky-700 hover:underline"
          >
            Продолжить в Telegram →
          </a>
        </div>
      ) : null}
    </ChatShell>
  );
}
