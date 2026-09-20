import { readFileSync } from "node:fs";

const readme = readFileSync("README.md", "utf8");
const required = [
  "## AI Bouncer demo",
  "works completely offline",
  "scripts/start_kev.sh",
  "scripts/start_semif.sh",
  "Docker-isolated demo",
  "host.docker.internal",
  "Recording workflow",
  "per-request model probabilities—not accuracy",
  "Ollama is not required",
];

for (const signal of required) {
  if (!readme.includes(signal)) throw new Error(`README.md is missing: ${signal}`);
}

console.log("AI Bouncer documentation verification passed");
