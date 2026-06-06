import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

interface ChatShellProps {
  children: ReactNode;
  className?: string;
  compact?: boolean;
}

export function ChatShell({ children, className, compact = false }: ChatShellProps) {
  return (
    <div
      className={cn(
        "aira-glass flex w-full flex-col overflow-hidden rounded-3xl border border-white/40 shadow-2xl",
        compact ? "h-[560px] max-h-[90vh]" : "h-[640px] max-h-[90vh]",
        className,
      )}
    >
      {children}
    </div>
  );
}
