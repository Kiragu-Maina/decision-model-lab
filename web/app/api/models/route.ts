import { z } from "zod";

import {
  allModelServiceStatuses,
  startModelService,
  stopModelService,
} from "@/lib/model-services";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const controlRequest = z.object({
  model: z.enum(["kev", "semif"]),
  action: z.enum(["start", "stop"]).default("start"),
});

export async function GET(): Promise<Response> {
  return Response.json(
    { services: await allModelServiceStatuses() },
    { headers: { "cache-control": "no-store" } },
  );
}

export async function POST(request: Request): Promise<Response> {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return Response.json(
      { error: "Request body must be valid JSON." },
      { status: 400 },
    );
  }

  const parsed = controlRequest.safeParse(body);
  if (!parsed.success) {
    return Response.json({ error: "Choose Kev or SemIf." }, { status: 422 });
  }

  if (
    request.headers.get("x-ai-bouncer-control") !==
    `${parsed.data.action}-model`
  ) {
    return Response.json(
      { error: `Model ${parsed.data.action} request was not authorized.` },
      { status: 403 },
    );
  }

  try {
    const service =
      parsed.data.action === "start"
        ? await startModelService(parsed.data.model)
        : await stopModelService(parsed.data.model);
    return Response.json(
      { service },
      {
        status:
          service.state === "running" || service.state === "offline"
            ? 200
            : 202,
      },
    );
  } catch (error) {
    return Response.json(
      {
        error:
          error instanceof Error
            ? error.message
            : `The model could not be ${parsed.data.action}ed.`,
      },
      { status: 409 },
    );
  }
}
