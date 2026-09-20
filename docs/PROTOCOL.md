# Protocol

## Request contract

The HTTP backend sends `POST /v1/systemone` with the public TypeSafe-shaped
request:

```json
{
  "model": "local",
  "state": {"message": "I was charged twice."},
  "questions": {
    "team": {
      "type": "choice",
      "instructions": "Which team should handle this?",
      "criteria": {
        "billing": "charges and refunds",
        "technical": "bugs and outages"
      }
    },
    "refund": {
      "type": "noul",
      "instructions": "Does the message request a refund?"
    },
    "urgency": {
      "type": "score",
      "instructions": "How urgent is the request?",
      "criteria": ["routine", "time-sensitive", "blocking"]
    }
  }
}
```

Question identifiers are bookkeeping keys. A backend should not treat their
wording as part of the semantic prompt.

## Question primitives

### `choice`

The model selects exactly one caller-defined key and returns a probability for
every key. Criteria descriptions may be strings, structured JSON, or null.

### `noul`

The model returns `noul`, interpreted as `P(true)`. The evaluator converts it
to the two-class distribution `{"false": 1-p, "true": p}`. A backend may
instead return an explicit two-class `probabilities` map.

### `score`

The criteria array is ordered from low to high. The returned probability keys
are the zero-based string indices. The scalar score is recomputed by the
evaluator as the probability-weighted expected index, so a provider cannot
improve its ordinal score by returning an inconsistent scalar.

## Response contract

```json
{
  "model": "local-model-id",
  "answers": {
    "team": {
      "type": "choice",
      "choice": "billing",
      "probabilities": {"billing": 0.91, "technical": 0.09}
    },
    "refund": {"type": "noul", "noul": 0.76},
    "urgency": {
      "type": "score",
      "probabilities": {"0": 0.2, "1": 0.7, "2": 0.1}
    }
  }
}
```

The evaluator rejects missing/extra questions, options outside the schema,
negative or non-finite probabilities, and zero probability mass. Small
floating-point normalization drift is accepted and normalized.

## Command adapter

A command adapter receives one JSON request on standard input with an added
`case_id`. It must write one response object on standard output and diagnostics
only to standard error. It is invoked without a shell. Command adapters are
executed sequentially to avoid hidden shared-state races.

## Replay format

Replay files contain one JSON object per line:

```json
{"case_id":"routing-01","latency_ms":42.1,"response":{"model":"x","answers":{}}}
```

Replay latency is reported as captured; use `-1` when no valid measurement is
available. Never compare live latency with replay latency without matching the
hardware, transport, concurrency, warm-up policy, and repetition count.

