"use client";

import { useState } from "react";
import { Brain, Check, ChevronDown, Loader2 } from "lucide-react";

import { cn } from "@/lib/utils";
import type { AgentStep } from "@/lib/types/chat";

interface ThinkingPanelProps {
  steps: AgentStep[];
  isStreaming: boolean;
}

export function ThinkingPanel({ steps, isStreaming }: ThinkingPanelProps) {
  const [isOpen, setIsOpen] = useState(true);

  if (steps.length === 0) {
    return null;
  }

  return (
    <section className="mx-4 rounded-2xl border border-sky-100/80 bg-sky-50/70 p-3">
      <button
        type="button"
        onClick={() => setIsOpen((value) => !value)}
        className="flex w-full items-center justify-between text-left"
      >
        <span className="flex items-center gap-2 text-sm font-medium text-slate-700">
          <Brain className="size-4 text-sky-600" />
          Думаю вслух
        </span>
        <ChevronDown
          className={cn(
            "size-4 text-slate-500 transition-transform",
            isOpen ? "rotate-180" : "",
          )}
        />
      </button>
      {isOpen ? (
        <ul className="mt-3 space-y-2">
          {steps.map((step) => (
            <li key={step.id} className="flex items-start gap-2 text-sm text-slate-700">
              <StepIcon status={step.status} isStreaming={isStreaming} />
              <span
                className={cn(
                  step.status === "active" && "font-medium text-slate-900",
                  step.status === "pending" && "text-slate-500",
                )}
              >
                {step.label}
              </span>
            </li>
          ))}
        </ul>
      ) : null}
    </section>
  );
}

function StepIcon({
  status,
  isStreaming,
}: {
  status: AgentStep["status"];
  isStreaming: boolean;
}) {
  if (status === "done") {
    return <Check className="mt-0.5 size-4 shrink-0 text-emerald-500" />;
  }
  if (status === "active" && isStreaming) {
    return <Loader2 className="mt-0.5 size-4 shrink-0 animate-spin text-sky-500" />;
  }
  return (
    <span className="mt-1 size-3 shrink-0 rounded-full border-2 border-slate-300" />
  );
}
