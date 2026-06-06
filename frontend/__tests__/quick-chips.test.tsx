import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { QuickChips } from "@/components/chat/quick-chips";

describe("QuickChips", () => {
  it("calls onSelect with preset message", async () => {
    const user = userEvent.setup();
    const onSelect = vi.fn();

    render(<QuickChips onSelect={onSelect} />);
    await user.click(screen.getByRole("button", { name: /Курсы для новичков/i }));

    expect(onSelect).toHaveBeenCalledWith("Какой курс для новичка?");
  });
});
