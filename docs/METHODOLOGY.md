# Methodology

## What the suite measures

The benchmark separates five concerns that are often collapsed into one
accuracy number:

1. Semantic decision quality.
2. Probability quality and calibration.
3. Robustness to presentation changes.
4. Protocol reliability.
5. End-to-end latency in the selected deployment topology.

## Core metrics

- **Accuracy:** whether the highest-probability option matches the highest-mass
  gold option. Useful but insensitive to probability quality.
- **Soft accuracy:** dot product between predicted and gold distributions.
  Ambiguous cases reward probability mass on plausible alternatives.
- **Brier score:** squared distance between predicted and gold distributions;
  lower is better.
- **Log loss:** cross-entropy against hard or soft gold distributions; lower is
  better and strongly penalizes confident errors.
- **ECE:** ten-bin expected calibration error over all valid decisions; lower
  is better. For soft targets, the calibration target is the gold probability
  assigned to the model's selected option rather than a forced binary label.
  Treat small differences cautiously on this corpus size.
- **Score MAE:** absolute error between predicted and gold expected ordinal
  level for `score` questions.
- **Selective accuracy:** accuracy and coverage at confidence thresholds 0.5,
  0.7, and 0.9. This reveals whether confidence can safely route uncertain
  cases to review.

## Stability tests

Variants preserve the underlying answer while changing one surface property:

- **option-order:** reverse caller-defined Choice option order;
- **question-order:** reverse questions within the shared-state request;
- **paraphrase:** replace instructions with a semantically equivalent wording;
- **irrelevant-context:** append unrelated information.

For every aligned pair, the suite reports selection agreement and total
variation distance between probability distributions. A model can therefore
retain the same top choice while still exposing unstable probabilities.

## Corpus construction

Cases are authored from explicit local facts and rules. The suite does not use
Jev, kev, SemIf, or another model to create ground-truth labels. Hard targets
represent deterministic facts or policies. The ambiguity slice uses authored
soft distributions and is scored primarily with proper scoring rules.

Generated transformations are deterministic and live in
`src/jevbench/corpus.py`. The report records a SHA-256 digest of the exact
selected cases, questions, options, expectations, ordering, and metadata.

## Fair comparison rules

- Compare reports only when corpus digests match.
- Record whether a model trained on any corpus family. In-domain and transfer
  results must not be merged into one claim.
- Use the same request serialization, option descriptions, repetition count,
  concurrency, and timeout.
- Warm models before a latency run, or identify the measurement as cold.
- Do not compare a host-native Metal measurement with a CPU-only Docker run.
- Concurrent throughput uses total wall-clock run time; per-case p50 and p95
  continue to use the individual request measurements returned by the runner.
- Report schema failures and timeouts as errors, never silently drop them.
- Treat a temperature fitted on this test corpus as test leakage. Calibration
  must be fixed before final evaluation.

## Limitations

The corpus is an engineering diagnostic, not a claim of universal intelligence.
It is English-centric, compact, and mostly synthetic. Some slices measure rule
following more than world knowledge. Confidence estimates require validation
on the actual deployment distribution before consequential automation.
