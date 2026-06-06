import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ThinkingPanel } from "@/components/chat/thinking-panel";

describe("ThinkingPanel", () => {
  it("renders step statuses", () => {
    render(
      <ThinkingPanel
        isStreaming
        steps={[
          { id: "1", label: "Анализирую запрос", status: "done" },
          { id: "2", label: "Ищу курсы", status: "active" },
          { id: "3", label: "Готовлю ответ", status: "pending" },
        ]}
      />,
    );

    expect(screen.getByText("Думаю вслух")).toBeInTheDocument();
    expect(screen.getByText("Анализирую запрос")).toBeInTheDocument();
    expect(screen.getByText("Ищу курсы")).toBeInTheDocument();
    expect(screen.getByText("Готовлю ответ")).toBeInTheDocument();
  });
});
