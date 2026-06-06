"use client";

import { FormEvent, useState } from "react";
import { Send } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled = false }: ChatInputProps) {
  const [value, setValue] = useState("");

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || disabled) {
      return;
    }
    onSend(trimmed);
    setValue("");
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex items-center gap-2 border-t border-white/30 bg-white/30 px-4 py-3"
    >
      <Input
        value={value}
        onChange={(event) => setValue(event.target.value)}
        placeholder="Задайте вопрос..."
        disabled={disabled}
        className="h-11 flex-1 border-white/50 bg-white/80"
      />
      <Button
        type="submit"
        disabled={disabled || !value.trim()}
        className="aira-gradient size-11 shrink-0 rounded-full border-0 p-0 text-white shadow-md hover:opacity-90"
        aria-label="Отправить"
      >
        <Send className="size-4" />
      </Button>
    </form>
  );
}
