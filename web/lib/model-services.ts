import { closeSync, existsSync, mkdirSync, openSync } from "node:fs";
import { connect } from "node:net";
import { resolve } from "node:path";
import { execFileSync, spawn } from "node:child_process";

import type { ModelId, ModelServiceStatus } from "./contracts";

interface ServiceDefinition {
  label: string;
  env: "KEV_BASE_URL" | "SEMIF_BASE_URL";
  fallback: string;
  script: "start_kev.sh" | "start_semif.sh";
  processSignature: string;
}

interface LaunchRecord {
  state: "starting" | "running" | "stopping" | "error";
  startedAt: number;
  pid?: number;
  message?: string;
}

const definitions: Record<ModelId, ServiceDefinition> = {
  kev: {
    label: "Kev 0.5B",
    env: "KEV_BASE_URL",
    fallback: "http://127.0.0.1:8009",
    script: "start_kev.sh",
    processSignature: "kev.serve",
  },
  semif: {
    label: "SemIf Qwen3.5 4B",
    env: "SEMIF_BASE_URL",
    fallback: "http://127.0.0.1:8011",
    script: "start_semif.sh",
    processSignature: "semif_server.py",
  },
};

const launchRecords = globalThis as typeof globalThis & {
  __aiBouncerModelLaunches?: Partial<Record<ModelId, LaunchRecord>>;
};

const records =
  launchRecords.__aiBouncerModelLaunches ??
  (launchRecords.__aiBouncerModelLaunches = {});

function endpointFor(model: ModelId): URL {
  const definition = definitions[model];
  return new URL(process.env[definition.env] || definition.fallback);
}

function projectRoot(): string | null {
  const candidates = [
    process.env.AI_BOUNCER_PROJECT_ROOT,
    process.cwd(),
    resolve(process.cwd(), ".."),
  ].filter((candidate): candidate is string => Boolean(candidate));
  return (
    candidates.find((candidate) =>
      existsSync(resolve(candidate, "scripts", "start_kev.sh")),
    ) ?? null
  );
}

function isLoopback(hostname: string): boolean {
  return (
    hostname === "127.0.0.1" || hostname === "localhost" || hostname === "::1"
  );
}

function launchSupport(model: ModelId): { ok: boolean; reason: string } {
  const endpoint = endpointFor(model);
  if (process.platform !== "darwin") {
    return {
      ok: false,
      reason: "Start controls are available only from the native macOS server.",
    };
  }
  if (!isLoopback(endpoint.hostname)) {
    return {
      ok: false,
      reason:
        "This endpoint is external to the app process; start it on its host.",
    };
  }
  const root = projectRoot();
  if (
    !root ||
    !existsSync(resolve(root, "scripts", definitions[model].script))
  ) {
    return {
      ok: false,
      reason: "Native model launch scripts are not present in this runtime.",
    };
  }
  return { ok: true, reason: "Ready to start on this Mac." };
}

function endpointOpen(endpoint: URL, timeoutMs = 450): Promise<boolean> {
  const port = Number(
    endpoint.port || (endpoint.protocol === "https:" ? 443 : 80),
  );
  return new Promise((resolveOpen) => {
    const socket = connect({ host: endpoint.hostname, port });
    let settled = false;
    const finish = (open: boolean) => {
      if (settled) return;
      settled = true;
      socket.destroy();
      resolveOpen(open);
    };
    socket.setTimeout(timeoutMs);
    socket.once("connect", () => finish(true));
    socket.once("timeout", () => finish(false));
    socket.once("error", () => finish(false));
  });
}

function processExists(pid: number): boolean {
  try {
    process.kill(pid, 0);
    return true;
  } catch {
    return false;
  }
}

function directChildServing(model: ModelId, endpoint: URL): number | undefined {
  if (process.platform !== "darwin") return undefined;
  const port = endpoint.port || (endpoint.protocol === "https:" ? "443" : "80");
  try {
    const listeners = execFileSync(
      "lsof",
      ["-nP", "-t", `-iTCP:${port}`, "-sTCP:LISTEN"],
      { encoding: "utf8", timeout: 500 },
    )
      .trim()
      .split(/\s+/)
      .map(Number)
      .filter(Number.isInteger);

    return listeners.find((pid) => {
      const processLine = execFileSync(
        "ps",
        ["-p", String(pid), "-o", "ppid=,command="],
        { encoding: "utf8", timeout: 500 },
      ).trim();
      const match = processLine.match(/^(\d+)\s+(.+)$/);
      return (
        Number(match?.[1]) === process.pid &&
        match?.[2].includes(definitions[model].processSignature)
      );
    });
  } catch {
    return undefined;
  }
}

export async function modelServiceStatus(
  model: ModelId,
): Promise<ModelServiceStatus> {
  const endpoint = endpointFor(model);
  const open = await endpointOpen(endpoint);
  const support = launchSupport(model);
  let record = records[model];

  if (open) {
    if (record?.state === "stopping") {
      return {
        model,
        label: definitions[model].label,
        endpoint: endpoint.origin,
        state: "stopping",
        launchable: support.ok,
        stoppable: false,
        message: "Waiting for the local process to release its port…",
      };
    }
    const recoveredPid =
      record?.pid && processExists(record.pid)
        ? record.pid
        : directChildServing(model, endpoint);
    if (recoveredPid && record?.pid !== recoveredPid) {
      records[model] = {
        state: "running",
        startedAt: Date.now(),
        pid: recoveredPid,
      };
      record = records[model];
    }
    const owned = Boolean(recoveredPid);
    if (owned && record) record.state = "running";
    return {
      model,
      label: definitions[model].label,
      endpoint: endpoint.origin,
      state: "running",
      launchable: support.ok,
      stoppable: owned,
      message: owned
        ? "Accepting requests — started by this app."
        : "Accepting requests — managed outside this app.",
    };
  }

  if (record?.state === "stopping") delete records[model];

  if (record?.state === "starting" && Date.now() - record.startedAt < 180_000) {
    return {
      model,
      label: definitions[model].label,
      endpoint: endpoint.origin,
      state: "starting",
      launchable: support.ok,
      stoppable: false,
      message: "Loading weights into memory…",
    };
  }

  if (record?.state === "error") {
    return {
      model,
      label: definitions[model].label,
      endpoint: endpoint.origin,
      state: "error",
      launchable: support.ok,
      stoppable: false,
      message:
        record.message || "The model process exited before becoming ready.",
    };
  }

  return {
    model,
    label: definitions[model].label,
    endpoint: endpoint.origin,
    state: "offline",
    launchable: support.ok,
    stoppable: false,
    message: support.ok
      ? "Stopped — start it when live inference is needed."
      : support.reason,
  };
}

export async function allModelServiceStatuses(): Promise<ModelServiceStatus[]> {
  return Promise.all([modelServiceStatus("kev"), modelServiceStatus("semif")]);
}

export async function startModelService(
  model: ModelId,
): Promise<ModelServiceStatus> {
  const current = await modelServiceStatus(model);
  if (current.state === "running" || current.state === "starting")
    return current;

  const support = launchSupport(model);
  const root = projectRoot();
  if (!support.ok || !root) throw new Error(support.reason);

  const logsDirectory = resolve(root, ".models", "logs");
  mkdirSync(logsDirectory, { recursive: true });
  const logPath = resolve(logsDirectory, `${model}.log`);
  const logDescriptor = openSync(logPath, "a");
  const scriptPath = resolve(root, "scripts", definitions[model].script);
  let child;
  try {
    child = spawn(scriptPath, [], {
      cwd: root,
      detached: false,
      env: process.env,
      stdio: ["ignore", logDescriptor, logDescriptor],
    });
  } finally {
    closeSync(logDescriptor);
  }

  records[model] = {
    state: "starting",
    startedAt: Date.now(),
    pid: child.pid,
  };
  child.once("error", (error) => {
    records[model] = {
      state: "error",
      startedAt: Date.now(),
      pid: child.pid,
      message: error.message,
    };
  });
  child.once("exit", (code) => {
    const record = records[model];
    if (!record || record.pid !== child.pid) return;
    if (record.state === "stopping") {
      delete records[model];
    } else if (record.state === "starting" || record.state === "running") {
      records[model] = {
        state: "error",
        startedAt: Date.now(),
        message: `Process exited with code ${code ?? "unknown"}. See ${logPath}.`,
      };
    }
  });
  child.unref();

  return modelServiceStatus(model);
}

export async function stopModelService(
  model: ModelId,
): Promise<ModelServiceStatus> {
  const current = await modelServiceStatus(model);
  if (current.state === "offline" || current.state === "stopping") {
    return current;
  }

  const record = records[model];
  if (!record?.pid || !processExists(record.pid)) {
    throw new Error(
      "This model was not started by this app. Stop it from its terminal or process manager.",
    );
  }

  record.state = "stopping";
  record.startedAt = Date.now();
  try {
    process.kill(record.pid, "SIGTERM");
  } catch (error) {
    record.state = "error";
    record.message =
      error instanceof Error
        ? error.message
        : "The model process did not stop.";
    throw error;
  }

  return modelServiceStatus(model);
}
