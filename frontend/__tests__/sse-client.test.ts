import { readFileSync } from "node:fs";
import { join } from "node:path";

import { afterEach, describe, expect, it, vi } from "vitest";

import { parseSseBlocks, streamChat } from "@/lib/sse-client";
import { StreamError } from "@/lib/types/sse";

describe("parseSseBlocks", () => {
  it("parses multi-event payload", () => {
    const fixture = readFileSync(
      join(__dirname, "fixtures", "sse-events.txt"),
      "utf-8",
    );
    const { events, remainder } = parseSseBlocks(fixture);

    expect(remainder).toBe("");
    expect(events).toHaveLength(4);
    expect(events[0]?.type).toBe("agent_step");
    expect(events[1]?.type).toBe("token");
    expect(events[3]?.type).toBe("done");
  });

  it("buffers incomplete blocks", () => {
    const partial = 'event: token\ndata: {"text":"Hi"';
    const { events, remainder } = parseSseBlocks(partial);

    expect(events).toHaveLength(0);
    expect(remainder).toBe(partial);
  });
});

describe("streamChat", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("sends channel web in request body", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      headers: { get: () => "text/event-stream" },
      body: {
        getReader: () => ({
          read: async () => ({ done: true, value: undefined }),
        }),
      },
    });
    vi.stubGlobal("fetch", fetchMock);

    await streamChat({
      sessionId: "550e8400-e29b-41d4-a716-446655440000",
      message: "test",
      onEvent: () => undefined,
    });

    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(JSON.parse(String(init.body))).toEqual({
      session_id: "550e8400-e29b-41d4-a716-446655440000",
      channel: "web",
      message: "test",
    });
  });

  it("throws StreamError on pre-stream 503", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 503,
        headers: { get: () => "application/json" },
        json: async () => ({
          detail: { message: "Сервис ИИ временно недоступен" },
        }),
      }),
    );

    await expect(
      streamChat({
        sessionId: "550e8400-e29b-41d4-a716-446655440000",
        message: "test",
        onEvent: () => undefined,
      }),
    ).rejects.toBeInstanceOf(StreamError);
  });

  it("stops after in-stream error event", async () => {
    const payload = new TextEncoder().encode(
      'event: error\ndata: {"message":"fail"}\n\n',
    );
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        headers: { get: () => "text/event-stream" },
        body: {
          getReader: () => {
            let sent = false;
            return {
              read: async () => {
                if (sent) {
                  return { done: true, value: undefined };
                }
                sent = true;
                return { done: false, value: payload };
              },
            };
          },
        },
      }),
    );

    const events: string[] = [];
    await streamChat({
      sessionId: "550e8400-e29b-41d4-a716-446655440000",
      message: "test",
      onEvent: (event) => events.push(event.type),
    });

    expect(events).toEqual(["error"]);
  });

  it("respects AbortController", async () => {
    const controller = new AbortController();
    controller.abort();

    vi.stubGlobal(
      "fetch",
      vi.fn().mockRejectedValue(new DOMException("Aborted", "AbortError")),
    );

    await expect(
      streamChat({
        sessionId: "550e8400-e29b-41d4-a716-446655440000",
        message: "test",
        signal: controller.signal,
        onEvent: () => undefined,
      }),
    ).rejects.toThrow();
  });
});
