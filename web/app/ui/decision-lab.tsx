"use client";

import { useCallback, useEffect, useState } from "react";
import Image from "next/image";

import type {
  DimensionDecision,
  DimensionKey,
  EvaluationResponse,
  ModelId,
  ModelResult,
  ModelServiceStatus,
  Resolution,
  SourceMode,
} from "@/lib/contracts";
import { resolveVerdict } from "@/lib/decision";
import { scenarios } from "@/lib/scenarios";

const gateMeta: Array<{
  key: DimensionKey;
  number: string;
  name: string;
  question: string;
}> = [
  {
    key: "authorization",
    number: "01",
    name: "AUTHORIZATION",
    question: "Is the requester allowed?",
  },
  {
    key: "sensitivity",
    number: "02",
    name: "SENSITIVITY",
    question: "Could this be sensitive?",
  },
  {
    key: "reversibility",
    number: "03",
    name: "REVERSIBILITY",
    question: "Can we undo it?",
  },
  {
    key: "injection",
    number: "04",
    name: "INJECTION",
    question: "Is this user input trying to override?",
  },
  {
    key: "risk",
    number: "05",
    name: "RISK",
    question: "Is this overall risky?",
  },
];

const benchmark = {
  kev: { accuracy: "65.8%", latency: "78 ms" },
  semif: { accuracy: "86.1%", latency: "1,366 ms" },
};

const verdictCopy: Record<
  Resolution["verdict"],
  { label: string; reason: string }
> = {
  block: { label: "BLOCK", reason: "Hard safety boundary detected" },
  confirm: { label: "ASK HUMAN", reason: "Explicit approval required" },
  allow: { label: "ALLOW", reason: "Selected checks cleared" },
  unavailable: { label: "NO VERDICT", reason: "Model evidence unavailable" },
};

function replayResponse(scenarioIndex: number): EvaluationResponse {
  const results = Object.values(scenarios[scenarioIndex].replay);
  return {
    requestId: `replay-${scenarios[scenarioIndex].id}`,
    source: "replay",
    replay: true,
    results,
    failures: [],
    resolution: resolveVerdict(results, [], ["kev", "semif"]),
    safeSimulation: true,
  };
}

function requestedModels(source: SourceMode): ModelId[] {
  return source === "both" || source === "replay"
    ? ["kev", "semif"]
    : source === "semif"
      ? ["semif"]
      : ["kev"];
}

function pendingLiveResponse(
  source: Exclude<SourceMode, "replay">,
): EvaluationResponse {
  const requested = requestedModels(source);
  return {
    requestId: "awaiting-live-run",
    source,
    replay: false,
    results: [],
    failures: [],
    resolution: resolveVerdict([], [], requested),
    safeSimulation: true,
  };
}

const checkingServices: ModelServiceStatus[] = [
  {
    model: "kev",
    label: "Kev 0.5B",
    endpoint: "127.0.0.1:8009",
    state: "starting",
    launchable: false,
    stoppable: false,
    message: "Checking the local endpoint…",
  },
  {
    model: "semif",
    label: "SemIf Qwen3.5 4B",
    endpoint: "127.0.0.1:8011",
    state: "starting",
    launchable: false,
    stoppable: false,
    message: "Checking the local endpoint…",
  },
];

function ModelServices({
  services,
  pendingActions,
  error,
  onControl,
}: {
  services: ModelServiceStatus[];
  pendingActions: Partial<Record<ModelId, "start" | "stop">>;
  error: string;
  onControl: (model: ModelId, action: "start" | "stop") => void;
}) {
  const visibleServices = services.length
    ? checkingServices.map(
        (placeholder) =>
          services.find((service) => service.model === placeholder.model) ??
          placeholder,
      )
    : checkingServices;

  return (
    <div className="model-services" aria-label="Local model services">
      <div className="model-services-header">
        <strong>MODEL SERVICES</strong>
        <span>AUTO-REFRESH</span>
      </div>
      <div aria-live="polite">
        {visibleServices.map((service) => {
          const pendingAction = pendingActions[service.model];
          const isStarting =
            service.state === "starting" || pendingAction === "start";
          const isStopping =
            service.state === "stopping" || pendingAction === "stop";
          const action = service.state === "running" ? "stop" : "start";
          const disabled =
            isStarting ||
            isStopping ||
            (action === "start" ? !service.launchable : !service.stoppable);
          let buttonLabel = `START ${service.model.toUpperCase()}`;
          if (isStarting) buttonLabel = "STARTING…";
          else if (isStopping) buttonLabel = "STOPPING…";
          else if (service.state === "running" && service.stoppable)
            buttonLabel = `STOP ${service.model.toUpperCase()}`;
          else if (service.state === "running") buttonLabel = "EXTERNAL";
          else if (!service.launchable) buttonLabel = "HOST ONLY";

          return (
            <div className="model-service" key={service.model}>
              <div className="model-service-copy">
                <div className="model-service-title">
                  <span
                    className={`service-light service-light-${service.state}`}
                    aria-hidden="true"
                  />
                  <strong>{service.label}</strong>
                  <span
                    className={`service-state service-state-${service.state}`}
                  >
                    {isStarting
                      ? "STARTING"
                      : isStopping
                        ? "STOPPING"
                        : service.state.toUpperCase()}
                  </span>
                </div>
                <code>{service.endpoint}</code>
                <small>{service.message}</small>
              </div>
              <button
                type="button"
                disabled={disabled}
                onClick={() => onControl(service.model, action)}
                aria-label={`${buttonLabel}: ${service.label}`}
                className={action === "stop" ? "is-stop" : undefined}
              >
                {buttonLabel}
              </button>
            </div>
          );
        })}
      </div>
      {error ? (
        <p className="model-control-error" role="alert">
          {error}
        </p>
      ) : null}
    </div>
  );
}

function unsafeProbability(
  key: DimensionKey,
  decision: DimensionDecision,
): number {
  if (key === "authorization") {
    return (
      (decision.probabilities.forbidden ?? 0) +
      (decision.probabilities.needs_approval ?? 0)
    );
  }
  if (key === "sensitivity") {
    return (
      (decision.probabilities.restricted ?? 0) +
      (decision.probabilities.confidential ?? 0)
    );
  }
  if (key === "reversibility") return decision.probabilities.reversible ?? 0;
  if (key === "injection") return decision.probabilities.true ?? 0;
  return decision.probability;
}

function gateState(
  key: DimensionKey,
  decision?: DimensionDecision,
): "PASS" | "WARN" | "FAIL" | "OFF" {
  if (!decision) return "OFF";
  if (
    decision.selection === "forbidden" ||
    decision.selection === "restricted" ||
    decision.selection === "critical"
  ) {
    return "FAIL";
  }
  if (
    decision.selection === "needs_approval" ||
    decision.selection === "confidential" ||
    (decision.selection !== "reversible" &&
      decision.selection.includes("reversible")) ||
    decision.selection === "irreversible" ||
    decision.selection === "guarded" ||
    decision.selection === "high" ||
    (key === "injection" && unsafeProbability(key, decision) >= 0.45)
  ) {
    return "WARN";
  }
  return "PASS";
}

function Reading({
  model,
  decision,
  dimension,
}: {
  model: string;
  decision?: DimensionDecision;
  dimension: DimensionKey;
}) {
  const state = gateState(dimension, decision);
  const value = decision
    ? `${Math.round(unsafeProbability(dimension, decision) * 100)}%`
    : "—";
  return (
    <div className={`reading reading-${state.toLowerCase()}`}>
      <span
        className="model-name"
        title={`${model} model probability`}
        aria-label={`${model} model probability`}
      >
        {model}
      </span>
      <strong>{value}</strong>
      <span className="reading-state" aria-label={`Result: ${state}`}>
        <i aria-hidden="true" />
        {state}
      </span>
    </div>
  );
}

function Stage({
  scenarioIndex,
  response,
  status,
  activeStep,
  source,
  onEvidence,
}: {
  scenarioIndex: number;
  response: EvaluationResponse;
  status: "ready" | "inspecting" | "error";
  activeStep: number;
  source: SourceMode;
  onEvidence: () => void;
}) {
  const scenario = scenarios[scenarioIndex];
  const byModel = Object.fromEntries(
    response.results.map((result) => [result.model, result]),
  ) as Partial<Record<ModelId, ModelResult>>;
  const verdict = verdictCopy[response.resolution.verdict];
  const shortAction = scenario.stageAction;
  const confidence = response.results
    .map(
      (result) =>
        `${result.model.toUpperCase()} ${Math.round(result.confidence * 100)}%`,
    )
    .join(" · ");

  return (
    <section
      className={`comp-frame dive-stage verdict-${response.resolution.verdict} stage-${status}`}
      aria-label="AI Bouncer decision descent"
      aria-busy={status === "inspecting"}
    >
      <Image
        className="r-depth-background depth-background"
        src="/plates/depth-background.png"
        alt=""
        width={941}
        height={1672}
        priority
      />
      <div className="r-brand brand" aria-label="AI Bouncer">
        <span className="signal-mark" aria-hidden="true">
          <i />
          <i />
          <i />
          <i />
          <i />
        </span>
        <strong>AI BOUNCER</strong>
      </div>
      <div
        className={`r-replay replay-badge ${source === "replay" ? "is-replay" : "is-live"}`}
      >
        <span
          className={source === "replay" ? "icon-replay" : "icon-live"}
          aria-hidden="true"
        />
        {source === "replay" ? "REPLAY" : "LIVE"}
      </div>
      <p className="r-surface-label surface-label">SURFACE 000</p>
      <div className="r-action-start action-start">
        <div className="action-capsule action-capsule-start">
          <span className="icon-document" aria-hidden="true" />
          <strong>{shortAction}</strong>
        </div>
      </div>
      <div className="r-descent-tether descent-tether" aria-hidden="true">
        <span className="node node-1" />
        <span className="node node-2" />
        <span className="node node-3" />
        <span className="node node-4" />
        <span className="node node-5" />
        <span className="node node-6" />
      </div>

      {gateMeta.map((gate, index) => {
        const position = ["one", "two", "three", "four", "five"][index];
        return (
          <div
            key={gate.key}
            className={`gate gate-${position} ${status === "inspecting" && index < activeStep ? "is-resolved" : ""} ${status === "inspecting" && index === activeStep ? "is-active" : ""}`}
          >
            <div
              className={`r-gate-${position}-frame gate-frame`}
              aria-hidden="true"
            />
            <div className={`r-gate-${position}-label gate-label`}>
              <span className="gate-number">{gate.number}</span>
              <strong>{gate.name}</strong>
              <small>{gate.question}</small>
            </div>
            <div
              className={`r-gate-${position}-kev gate-reading gate-reading-kev`}
            >
              <Reading
                model="KEV"
                decision={byModel.kev?.dimensions[gate.key]}
                dimension={gate.key}
              />
            </div>
            <div
              className={`r-gate-${position}-semif gate-reading gate-reading-semif`}
            >
              <Reading
                model="SEMIF"
                decision={byModel.semif?.dimensions[gate.key]}
                dimension={gate.key}
              />
            </div>
          </div>
        );
      })}

      <div
        className="r-thermocline-frame thermocline-frame"
        aria-hidden="true"
      />
      <button
        className="r-hidden-evidence hidden-evidence"
        type="button"
        onClick={onEvidence}
      >
        <span className="icon-document" aria-hidden="true" />
        <span>{scenario.stageEvidence}</span>
      </button>
      <div className="r-caught-action caught-action">
        <div className="action-capsule action-capsule-caught">
          <span className="icon-document" aria-hidden="true" />
          <strong>{shortAction}</strong>
        </div>
      </div>
      <div className="r-turnaround-frame turnaround-frame" aria-hidden="true" />
      <p className="r-turnaround-label turnaround-label">
        {status === "inspecting" ? "DESCENDING" : "TURNAROUND"}
      </p>
      <div className="r-verdict verdict">
        <span className="block-symbol" aria-hidden="true" />
        <strong>{status === "inspecting" ? "INSPECT" : verdict.label}</strong>
      </div>
      <div className="r-verdict-reason verdict-reason">
        <p>
          {status === "inspecting"
            ? "Running structured checks…"
            : response.resolution.disagreement
              ? "Models disagree — human review"
              : response.resolution.verdict === "block"
                ? scenario.verdictReason
                : verdict.reason}
        </p>
        {confidence ? (
          <small className="confidence-line">
            MODEL CONFIDENCE · {confidence}
          </small>
        ) : null}
        <strong>ACTION NOT EXECUTED</strong>
      </div>
      <button
        className="r-review-evidence review-evidence"
        type="button"
        onClick={onEvidence}
      >
        <span className="icon-search" aria-hidden="true" />
        <strong>REVIEW EVIDENCE</strong>
        <span className="icon-arrow" aria-hidden="true" />
      </button>
    </section>
  );
}

export default function DecisionLab() {
  const [scenarioIndex, setScenarioIndex] = useState(0);
  const [source, setSource] = useState<SourceMode>("replay");
  const [draft, setDraft] = useState(() => ({
    action: scenarios[0].action,
    context: scenarios[0].context,
    policy: scenarios[0].policy,
  }));
  const [status, setStatus] = useState<"ready" | "inspecting" | "error">(
    "ready",
  );
  const [evidenceOpen, setEvidenceOpen] = useState(false);
  const [activeStep, setActiveStep] = useState(6);
  const [response, setResponse] = useState<EvaluationResponse>(() =>
    replayResponse(0),
  );
  const [modelServices, setModelServices] = useState<ModelServiceStatus[]>([]);
  const [pendingModelActions, setPendingModelActions] = useState<
    Partial<Record<ModelId, "start" | "stop">>
  >({});
  const [modelControlError, setModelControlError] = useState("");

  const refreshModelServices = useCallback(async () => {
    try {
      const result = await fetch("/api/models", { cache: "no-store" });
      if (!result.ok) throw new Error("Model status endpoint is unavailable.");
      const payload = (await result.json()) as {
        services: ModelServiceStatus[];
      };
      setModelServices(payload.services);
      setModelControlError("");
      setPendingModelActions((current) => {
        const next = { ...current };
        for (const service of payload.services) {
          if (service.state !== "starting" && service.state !== "stopping") {
            delete next[service.model];
          }
        }
        return next;
      });
    } catch (error) {
      setModelControlError(
        error instanceof Error ? error.message : "Could not read model status.",
      );
    }
  }, []);

  useEffect(() => {
    const initialPoll = window.setTimeout(() => void refreshModelServices(), 0);
    const poll = window.setInterval(() => void refreshModelServices(), 4_000);
    return () => {
      window.clearTimeout(initialPoll);
      window.clearInterval(poll);
    };
  }, [refreshModelServices]);

  async function controlModel(model: ModelId, action: "start" | "stop") {
    setPendingModelActions((current) => ({ ...current, [model]: action }));
    setModelControlError("");
    try {
      const result = await fetch("/api/models", {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "x-ai-bouncer-control": `${action}-model`,
        },
        body: JSON.stringify({ model, action }),
      });
      const payload = (await result.json()) as
        | { service: ModelServiceStatus }
        | { error: string };
      if (!("service" in payload)) throw new Error(payload.error);
      setModelServices((current) => [
        ...current.filter((service) => service.model !== model),
        payload.service,
      ]);
    } catch (error) {
      setModelControlError(
        error instanceof Error
          ? error.message
          : `The model could not ${action}.`,
      );
      setPendingModelActions((current) => {
        const next = { ...current };
        delete next[model];
        return next;
      });
    } finally {
      void refreshModelServices();
    }
  }

  function chooseScenario(index: number) {
    const next = scenarios[index];
    setScenarioIndex(index);
    setDraft({
      action: next.action,
      context: next.context,
      policy: next.policy,
    });
    setResponse(
      source === "replay" ? replayResponse(index) : pendingLiveResponse(source),
    );
    setStatus("ready");
    setActiveStep(6);
  }

  function chooseSource(nextSource: SourceMode) {
    setSource(nextSource);
    setResponse(
      nextSource === "replay"
        ? replayResponse(scenarioIndex)
        : pendingLiveResponse(nextSource),
    );
    setStatus("ready");
    setActiveStep(6);
  }

  async function runDescentAnimation() {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setActiveStep(6);
      return;
    }
    for (let step = 1; step <= 6; step += 1) {
      await new Promise((resolve) =>
        window.setTimeout(resolve, step === 6 ? 300 : 190),
      );
      setActiveStep(step);
    }
  }

  async function inspectAction() {
    setStatus("inspecting");
    setActiveStep(0);
    try {
      const [result] = await Promise.all([
        fetch("/api/evaluate", {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({
            scenarioId: scenarios[scenarioIndex].id,
            source,
            ...draft,
          }),
        }),
        runDescentAnimation(),
      ]);
      const payload = (await result.json()) as
        | EvaluationResponse
        | { error: string };
      if (!("safeSimulation" in payload)) throw new Error(payload.error);
      setResponse(payload);
      setStatus(payload.results.length ? "ready" : "error");
    } catch {
      const requested = requestedModels(source);
      setStatus("error");
      setResponse({
        requestId: "failed",
        source,
        replay: false,
        results: [],
        failures: [],
        resolution: resolveVerdict([], [], requested),
        safeSimulation: true,
      });
    }
  }

  return (
    <main className="app-shell">
      <div className="stage-column">
        <Stage
          scenarioIndex={scenarioIndex}
          response={response}
          status={status}
          activeStep={activeStep}
          source={source}
          onEvidence={() => setEvidenceOpen(true)}
        />
      </div>
      <aside className="control-deck" aria-label="Decision lab controls">
        <header className="deck-header">
          <h1>
            PUT AN AI ACTION
            <br />
            THROUGH THE DEPTHS.
          </h1>
          <p className="deck-intro">
            Small local models classify the action. A separate policy decides
            whether it passes. Dive values are per-request model probabilities;
            confidence and benchmark accuracy stay separately labeled.
          </p>
        </header>

        <section className="deck-section">
          <div className="section-heading">
            <span>01</span>
            <h2>CHOOSE THE TRAP</h2>
          </div>
          <div
            className="scenario-rail"
            role="list"
            aria-label="Prepared scenarios"
          >
            {scenarios.map((scenario, index) => (
              <button
                key={scenario.id}
                type="button"
                className={index === scenarioIndex ? "is-active" : ""}
                onClick={() => chooseScenario(index)}
              >
                <span>0{index + 1}</span>
                <strong>{scenario.title}</strong>
                <small>{scenario.kicker}</small>
              </button>
            ))}
          </div>
        </section>

        <section className="deck-section">
          <div className="section-heading">
            <span>02</span>
            <h2>SELECT THE BOUNCER</h2>
          </div>
          <div className="source-selector" aria-label="Evaluation source">
            {(["replay", "kev", "semif", "both"] as SourceMode[]).map(
              (mode) => (
                <button
                  type="button"
                  key={mode}
                  className={source === mode ? "is-active" : ""}
                  onClick={() => chooseSource(mode)}
                >
                  {mode === "both" ? "BOTH LIVE" : mode.toUpperCase()}
                </button>
              ),
            )}
          </div>
          <p className="source-note">
            {source === "replay"
              ? "Deterministic synthetic result — no model process required."
              : "Calls the selected host-native local model server."}
          </p>
          <ModelServices
            services={modelServices}
            pendingActions={pendingModelActions}
            error={modelControlError}
            onControl={controlModel}
          />
          <p className="accuracy-strip">
            FIXED TEST ACCURACY <strong>KEV 65.8%</strong>
            <strong>SEMIF 86.1%</strong>
          </p>
        </section>

        <section className="deck-section editor-section">
          <div className="section-heading">
            <span>03</span>
            <h2>INSPECT THE REQUEST</h2>
          </div>
          <label>
            <span>PROPOSED ACTION</span>
            <textarea
              value={draft.action}
              onChange={(event) =>
                setDraft({ ...draft, action: event.target.value })
              }
            />
          </label>
          <label>
            <span>CONTEXT / UNTRUSTED INPUT</span>
            <textarea
              value={draft.context}
              onChange={(event) =>
                setDraft({ ...draft, context: event.target.value })
              }
            />
          </label>
          <label>
            <span>POLICY</span>
            <textarea
              value={draft.policy}
              onChange={(event) =>
                setDraft({ ...draft, policy: event.target.value })
              }
            />
          </label>
          <button
            className="inspect-button"
            type="button"
            onClick={inspectAction}
            disabled={status === "inspecting"}
          >
            <span>
              {status === "inspecting" ? "DESCENDING…" : "INSPECT ACTION"}
            </span>
            <span className="icon-down" aria-hidden="true" />
          </button>
          <p className="safety-line">
            <span aria-hidden="true" /> SAFE SIMULATION · THIS APP NEVER
            EXECUTES THE ACTION
          </p>
        </section>

        <details
          className="technical-drawer"
          open={evidenceOpen}
          onToggle={(event) => setEvidenceOpen(event.currentTarget.open)}
        >
          <summary>
            <span>04</span> EVIDENCE &amp; BENCHMARK <i>+</i>
          </summary>
          <div className="drawer-body">
            <p className="evidence-callout">
              <strong>HIDDEN TRAP</strong>
              {scenarios[scenarioIndex].evidence}
            </p>
            {response.failures.map((failure) => (
              <p className="failure-callout" key={failure.model}>
                <strong>{failure.model.toUpperCase()} UNAVAILABLE</strong>
                {failure.message}
              </p>
            ))}
            <div className="benchmark-grid">
              <div>
                <span>KEV / TEST ACCURACY</span>
                <strong>{benchmark.kev.accuracy}</strong>
                <small>mean {benchmark.kev.latency}</small>
              </div>
              <div>
                <span>SEMIF / TEST ACCURACY</span>
                <strong>{benchmark.semif.accuracy}</strong>
                <small>mean {benchmark.semif.latency}</small>
              </div>
            </div>
            <p className="benchmark-note">
              Accuracy is from this repo&apos;s fixed 202-decision benchmark.
              Percentages on the dive are model probabilities for this
              request—not accuracy.
            </p>
          </div>
        </details>
      </aside>
    </main>
  );
}
