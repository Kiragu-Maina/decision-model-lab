import { readFileSync } from "node:fs";

const product = readFileSync("PRODUCT.md", "utf8");
const plan = readFileSync("docs/AI_BOUNCER_IMPLEMENTATION_PLAN.md", "utf8");

const productSignals = [
  "<!-- impeccable:product-schema 1 -->",
  "## Users",
  "## Product Purpose",
  "## Capabilities and Constraints",
  "## Evidence on Hand",
  "## Accessibility & Inclusion",
];

const planSignals = [
  "## 1. Outcome",
  "## 3. Scope",
  "## 4. System design",
  "### Decision contract",
  "## 6. Delivery phases",
  "## 7. Verification matrix",
  "## 8. Acceptance criteria",
  "Executing any represented action",
];

for (const signal of productSignals) {
  if (!product.includes(signal)) throw new Error(`PRODUCT.md is missing: ${signal}`);
}

for (const signal of planSignals) {
  if (!plan.includes(signal)) throw new Error(`implementation plan is missing: ${signal}`);
}

console.log("AI Bouncer plan verification passed");
