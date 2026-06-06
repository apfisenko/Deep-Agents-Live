import { Bot, MoreHorizontal, X } from "lucide-react";

interface ChatHeaderProps {
  onClose?: () => void;
  showClose?: boolean;
}

export function ChatHeader({ onClose, showClose = false }: ChatHeaderProps) {
  return (
    <header className="flex items-center justify-between border-b border-white/30 px-4 py-3">
      <div className="flex items-center gap-3">
        <div className="aira-gradient flex size-10 items-center justify-center rounded-full text-white shadow-md">
          <Bot className="size-5" />
        </div>
        <div>
          <p className="text-base font-semibold text-slate-800">Айра</p>
          <div className="flex items-center gap-1.5 text-xs text-slate-600">
            <span className="size-2 rounded-full bg-emerald-500" />
            <span>online</span>
          </div>
        </div>
      </div>
      <div className="flex items-center gap-1 text-slate-500">
        <button
          type="button"
          className="rounded-full p-1.5 hover:bg-white/40"
          aria-label="Меню"
        >
          <MoreHorizontal className="size-4" />
        </button>
        {showClose ? (
          <button
            type="button"
            onClick={onClose}
            className="rounded-full p-1.5 hover:bg-white/40"
            aria-label="Закрыть"
          >
            <X className="size-4" />
          </button>
        ) : null}
      </div>
    </header>
  );
}
