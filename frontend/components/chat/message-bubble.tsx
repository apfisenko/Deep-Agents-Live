import { cn } from "@/lib/utils";
import type { ChatMessage } from "@/lib/types/chat";

interface MessageBubbleProps {
  message: ChatMessage;
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString("ru-RU", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div className={cn("flex", isUser ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed shadow-sm",
          isUser
            ? "aira-gradient text-white"
            : "border border-white/50 bg-white/70 text-slate-800",
        )}
      >
        <p className="whitespace-pre-wrap">
          {message.content}
          {message.isStreaming ? (
            <span
              className="ml-0.5 inline-block h-4 w-0.5 animate-pulse bg-slate-500 align-middle"
              aria-hidden
            />
          ) : null}
        </p>
        <p
          className={cn(
            "mt-1 text-[10px]",
            isUser ? "text-white/80" : "text-slate-500",
          )}
        >
          {formatTime(message.createdAt)}
        </p>
      </div>
    </div>
  );
}
