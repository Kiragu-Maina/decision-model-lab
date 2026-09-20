# Corpus v1

The corpus is generated deterministically by `jevbench.corpus.build_corpus()`.
It contains authored scenario families plus mechanically generated paired
variants. Keeping the generator in source control makes every transformation
inspectable and avoids a large opaque fixture.

The suite covers:

- runtime-defined `choice`, `noul`, and ordinal `score` questions;
- routing, evidence, safety, policy, sentiment, long-context retrieval,
  ambiguity, abstention, and prompt-injection slices;
- paired option-order, question-order, paraphrase, and irrelevant-context
  perturbations;
- hard labels and soft target distributions;
- single-question and multi-question requests.

No model output is used as ground truth. Labels follow explicit facts or rules
embedded in each scenario. Ambiguous cases contain authored soft targets and
are scored with proper scoring rules rather than forced hard accuracy alone.

