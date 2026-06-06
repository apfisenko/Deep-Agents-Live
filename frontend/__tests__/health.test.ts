import { describe, expect, it } from "vitest";

import { GET } from "@/app/api/health/route";

describe("GET /api/health", () => {
  it("returns ok status", async () => {
    const response = await GET();
    const payload = (await response.json()) as { status: string; version: string };

    expect(response.status).toBe(200);
    expect(payload.status).toBe("ok");
    expect(payload.version).toBe("0.1.0");
  });
});
