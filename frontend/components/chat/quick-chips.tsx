interface QuickChipsProps {
  onSelect: (message: string) => void;
  disabled?: boolean;
}

const PRESETS = [
  { emoji: "🎓", label: "Курсы для новичков", message: "Какой курс для новичка?" },
  { emoji: "💳", label: "Сравнить цены", message: "Сравни цены на курсы" },
  { emoji: "❓", label: "Как купить?", message: "Как купить курс?" },
] as const;

export function QuickChips({ onSelect, disabled = false }: QuickChipsProps) {
  return (
    <div className="flex flex-wrap gap-2 px-4 pb-2">
      {PRESETS.map((preset) => (
        <button
          key={preset.label}
          type="button"
          disabled={disabled}
          onClick={() => onSelect(preset.message)}
          className="rounded-full border border-white/60 bg-white/70 px-3 py-1.5 text-xs font-medium text-slate-700 shadow-sm transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-50"
        >
          <span className="mr-1">{preset.emoji}</span>
          {preset.label}
        </button>
      ))}
    </div>
  );
}
