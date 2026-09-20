import assert from "node:assert/strict";
import test from "node:test";

import { POST } from "../app/api/models/route";

test("model start rejects requests without the local control header", async () => {
  const response = await POST(
    new Request("http://localhost/api/models", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ model: "kev" }),
    }),
  );

  assert.equal(response.status, 403);
});

test("model start accepts only the fixed model allowlist", async () => {
  const response = await POST(
    new Request("http://localhost/api/models", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-ai-bouncer-control": "start-model",
      },
      body: JSON.stringify({ model: "anything-else" }),
    }),
  );

  assert.equal(response.status, 422);
});

test("stop requests require the matching control header", async () => {
  const response = await POST(
    new Request("http://localhost/api/models", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-ai-bouncer-control": "start-model",
      },
      body: JSON.stringify({ model: "kev", action: "stop" }),
    }),
  );

  assert.equal(response.status, 403);
});
