# Gates: comprehensive Jev-style decision benchmark

OWNS: GATES.md, PRODUCT.md, DESIGN.md, README.md, LICENSE, pyproject.toml, Dockerfile, docker-compose.yml, .dockerignore, .gitignore, src/**, tests/**, corpus/**, docs/**, scripts/**, adapters/**, reports/**, web/**, .impeccable/**, .models/**, .venvs/**

Scope: deliver a reproducible, backend-neutral benchmark suite that runs in Docker while Apple-Silicon model servers remain host-native.

- [x] G0: the gate ledger contains mechanically sound completion checks
  CHECK: node /Users/kiragu/.agents/skills/unlazy/scripts/gate-lint.mjs GATES.md
  EXPECT: LINT OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=5d08444aab603cf2b1f5b322489eae0870405ae94613fa028d8c723c9a096896; exit=0; EXPECT=matched; output-sha256=48630b7361dd44ee870917b12c3d19b9d7bdea738aaca16bb04d4cab83b772d2; output-bytes=8; shell=/bin/sh; cwd=/Users/kiragu/Documents/crafting/jev-like-ai; path=ae60f164de85/21 entries

- [x] G1: the versioned corpus is structurally valid, balanced across required capabilities, and its validator rejects a known-invalid control
  CHECK: PYTHONPATH=src python3 scripts/verify_corpus.py
  EXPECT: corpus verification passed
  EVIDENCE: automatic-evidence=v1; definition-sha256=f86c9915a5441a82e683d99cb3894807807695ff82c544d8682d299662ac94c5; exit=0; EXPECT=matched; output-sha256=9194d279ee8076b3c5fde572b2da8e353981c420b520b9d89c4ddea2b793a4e7; output-bytes=27; shell=/bin/sh; cwd=/Users/kiragu/Documents/crafting/jev-like-ai; path=ae60f164de85/21 entries

- [x] G2: metric, protocol, perturbation, adapter, and reporting unit tests pass
  CHECK: PYTHONPATH=src python3 scripts/run_tests.py
  EXPECT: benchmark unit tests passed
  EVIDENCE: automatic-evidence=v1; definition-sha256=5077d1f6e21c1cad28d56559dec7c67617edacd78a1a8a5d9eee8ba44024f828; exit=0; EXPECT=matched; output-sha256=78050ce0684f243fa5b4111ad142fa64db625108f533a057a4789e37f10297bf; output-bytes=2277; shell=/bin/sh; cwd=/Users/kiragu/Documents/crafting/jev-like-ai; path=ae60f164de85/21 entries

- [x] G3: an end-to-end mock benchmark produces a validated machine-readable report and human summary
  CHECK: PYTHONPATH=src python3 scripts/smoke_benchmark.py
  EXPECT: smoke benchmark passed
  EVIDENCE: automatic-evidence=v1; definition-sha256=9f15e2bcd9bb2ac092796400f2f0f2fb715e969d6487d164928f1365c1e49ddc; exit=0; EXPECT=matched; output-sha256=07ce7101ffccf732c563ccecb11e65532521cc04258a14c86be075fb421e1580; output-bytes=23; shell=/bin/sh; cwd=/Users/kiragu/Documents/crafting/jev-like-ai; path=ae60f164de85/21 entries

- [x] G4: the Docker Compose configuration resolves with a host-native model endpoint and an isolated evaluator service
  CHECK: docker compose config
  EXPECT: host.docker.internal
  EVIDENCE: automatic-evidence=v1; definition-sha256=e0ee7b8cb3bb4c12c3e3fe7d9ef0808be3589aabb77a25824683993c5d6abe3d; exit=0; EXPECT=matched; output-sha256=4d92fec004f21edf706c904400bd1ba103c2a6cd9c299a0c52f9f49d3783e4c0; output-bytes=723; shell=/bin/sh; cwd=/Users/kiragu/Documents/crafting/jev-like-ai; path=ae60f164de85/21 entries

- [x] G5: the isolated Docker evaluator image builds and validates the complete corpus
  CHECK: docker compose run --build --rm evaluator validate
  EXPECT: corpus_version
  EVIDENCE: automatic-evidence=v1; definition-sha256=1a23df34d7989e236a4280886fe232abda93ea4366c72f36194d41d3862d3d99; exit=0; EXPECT=matched; output-sha256=cf9c07fbe9cc0aa9b7c3b51cfdb8af8b405bceb626ebb56cfb0547718f9c790d; output-bytes=4020; shell=/bin/sh; cwd=/Users/kiragu/Documents/crafting/jev-like-ai; path=ae60f164de85/21 entries

- [x] G6: repository documentation and packaged CLI expose corpus validation, dry-run, execution, comparison, and Docker workflows
  CHECK: PYTHONPATH=src python3 scripts/verify_docs.py
  EXPECT: documentation verification passed
  EVIDENCE: automatic-evidence=v1; definition-sha256=2c4a2a1da653812554198fae61909ebfb171156fb149778b25608aeb7a3d9897; exit=0; EXPECT=matched; output-sha256=5fdf546167baf5bdc4f619c1af10c1e37213d323a8196b34f4125c38449975d3; output-bytes=34; shell=/bin/sh; cwd=/Users/kiragu/Documents/crafting/jev-like-ai; path=ae60f164de85/21 entries

- [x] G7: the captured Docker-to-host SemIf MLX probe contains a protocol-valid typed decision response
  CHECK: PYTHONPATH=src python3 scripts/verify_probe_report.py reports/semif-docker-probe.json --expect-model semif-qwen3.5-4b-mlx
  EXPECT: probe report verified: semif-qwen3.5-4b-mlx
  EVIDENCE: automatic-evidence=v1; definition-sha256=9e5786a66bcd70bedc39570c1f2467384af353fcf102bc2f3d178c62b6e396b1; exit=0; EXPECT=matched; output-sha256=65e439b04d49be99652be4c86c993178d2d66457f9ace9067c3726cb18ab3efa; output-bytes=44; shell=/bin/sh; cwd=/Users/kiragu/Documents/crafting/jev-like-ai; path=ae60f164de85/21 entries

- [x] G8: the captured Docker-to-host kev-0.5b probe contains a protocol-valid typed decision response
  CHECK: PYTHONPATH=src python3 scripts/verify_probe_report.py reports/kev-docker-probe.json --expect-model kev-0.5b
  EXPECT: probe report verified: kev-0.5b
  EVIDENCE: automatic-evidence=v1; definition-sha256=7e3b9d0502ce8b9206cfd4768a82354e7c3c43ebfcd8e838efd051c03bc3b0e1; exit=0; EXPECT=matched; output-sha256=79d2330bef25aaaf9c8c37ca0e11197dd1d11727f90ca860113ce652470eb0c1; output-bytes=32; shell=/bin/sh; cwd=/Users/kiragu/Documents/crafting/jev-like-ai; path=ae60f164de85/21 entries

- [x] G9: the SemIf benchmark report covers every corpus decision without backend errors and binds to the versioned corpus digest
  CHECK: PYTHONPATH=src python3 scripts/verify_model_report.py reports/semif-qwen3.5-4b-mlx.json --expect-model semif-qwen3.5-4b-mlx --expect-repetitions 3
  EXPECT: model report verified: semif-qwen3.5-4b-mlx
  EVIDENCE: automatic-evidence=v1; definition-sha256=1eef5741784df391355f6f47f55924c9628791d605f73ace44be6a3f66a78135; exit=0; EXPECT=matched; output-sha256=e233af28faa87c230ec60a920d3a03ce774d6c8ebd08a21f523be65421dc1fd8; output-bytes=44; shell=/bin/sh; cwd=/Users/kiragu/Documents/crafting/jev-like-ai; path=ae60f164de85/21 entries

- [x] G10: the kev benchmark report covers every corpus decision without backend errors and binds to the versioned corpus digest
  CHECK: PYTHONPATH=src python3 scripts/verify_model_report.py reports/kev-0.5b.json --expect-model kev-0.5b --expect-repetitions 3
  EXPECT: model report verified: kev-0.5b
  EVIDENCE: automatic-evidence=v1; definition-sha256=855e0b8f3a1d2be914a372b77516f67ef2e84de00e64103a9572d3c7c21c5ddb; exit=0; EXPECT=matched; output-sha256=12063eb25ca97898d7997bf4dca7512efdc6ef4ae0c00da01ef21413bf2f5430; output-bytes=32; shell=/bin/sh; cwd=/Users/kiragu/Documents/crafting/jev-like-ai; path=ae60f164de85/21 entries

- [x] G11: the comparison is generated only from digest-compatible complete reports and names both contenders
  CHECK: PYTHONPATH=src python3 scripts/verify_comparison.py reports/comparison.json reports/semif-qwen3.5-4b-mlx.json reports/kev-0.5b.json
  EXPECT: comparison verified: semif-qwen3.5-4b-mlx vs kev-0.5b
  EVIDENCE: automatic-evidence=v1; definition-sha256=f3b91521cdc93eb31f8da455b183c9c06bd29424c9ebe2b6711fdbdc5abdcabe; exit=0; EXPECT=matched; output-sha256=e87011de4ac7a7dbab859dbeb6356929d2f374635a8c668a4f1f73f52f0bea9f; output-bytes=54; shell=/bin/sh; cwd=/Users/kiragu/Documents/crafting/jev-like-ai; path=ae60f164de85/21 entries

- [x] G12: all benchmark unit tests still pass after adding real-model adapters and report verification
  CHECK: PYTHONPATH=src python3 scripts/run_tests.py
  EXPECT: benchmark unit tests passed
  EVIDENCE: automatic-evidence=v1; definition-sha256=5077d1f6e21c1cad28d56559dec7c67617edacd78a1a8a5d9eee8ba44024f828; exit=0; EXPECT=matched; output-sha256=89b846f0801118a6f65c10fed6a4fa8e062676fe92bfe809900b200d5d889475; output-bytes=2277; shell=/bin/sh; cwd=/Users/kiragu/Documents/crafting/jev-like-ai; path=ae60f164de85/21 entries

- [x] G13: the AI Bouncer product brief and implementation plan define the audience, safety boundary, architecture, milestones, and acceptance criteria
  CHECK: node scripts/verify_ai_bouncer_plan.mjs
  EXPECT: AI Bouncer plan verification passed
  EVIDENCE: automatic-evidence=v1; definition-sha256=d59eb7b8f0285b99806e57e4a0fe9a0b43aa814fde6e39ab34ee0d6192d07b64; exit=0; EXPECT=matched; output-sha256=e37245fb5a0c8636aa16113c0ff86ea8e638019f79e9465830e4963e1ee5c102; output-bytes=36; shell=/bin/sh; cwd=/Users/kiragu/Documents/crafting/jev-like-ai; path=ae60f164de85/21 entries

- [x] G14: the Next.js application passes formatting, lint, and TypeScript checks
  CHECK: npm --prefix web run check
  EXPECT: web quality checks passed
  EVIDENCE: automatic-evidence=v1; definition-sha256=feadd3c90a44abba7a861ec4292536ab8f79d2ba4c2303b96dcf98e3bd08fd11; exit=0; EXPECT=matched; output-sha256=ff6d8b204da2a3bf53cba5fab07e9584f122e9e925fdf21f7ce183d667c3bba7; output-bytes=373; shell=/bin/sh; cwd=/Users/kiragu/Documents/crafting/jev-like-ai; path=ae60f164de85/21 entries

- [x] G15: decision aggregation and replay fixtures pass their unit and contract tests, including malformed-input and unavailable-model paths
  CHECK: npm --prefix web run test
  EXPECT: web tests passed
  EVIDENCE: automatic-evidence=v1; definition-sha256=2075a946da723bb333fb7169fed79ab52f2e084363ce71d904ba066e1b7118cb; exit=0; EXPECT=matched; output-sha256=4fa1ab6e33eafffdc7fee25a1814d6218d5fb9e843e995631d161f51d46875c1; output-bytes=825; shell=/bin/sh; cwd=/Users/kiragu/Documents/crafting/jev-like-ai; path=ae60f164de85/21 entries

- [x] G16: the production Next.js bundle compiles successfully
  CHECK: npm --prefix web run verify:build
  EXPECT: web production build passed
  EVIDENCE: automatic-evidence=v1; definition-sha256=de30924df4c7c3cb016c818b43ceb36f140d0bbeb85b27b9e82a7895867d7cd2; exit=0; EXPECT=matched; output-sha256=e954450a902825d9dffee05a887bbe8e2b5c833e81d2bb47f0d5dce4556130d4; output-bytes=820; shell=/bin/sh; cwd=/Users/kiragu/Documents/crafting/jev-like-ai; path=ae60f164de85/21 entries

- [x] G17: a production-server smoke test verifies the main page, replay evaluation, validation failure, and graceful live-backend failure
  CHECK: npm --prefix web run smoke
  EXPECT: web runtime smoke passed
  EVIDENCE: automatic-evidence=v1; definition-sha256=0318848572ed1751b179127cd8ced91563d46cd0cd4cb4b4b4e56b49698c5f52; exit=0; EXPECT=matched; output-sha256=c8ec15d7937b51ad0d376d06e132d63f9bccb757b2bdd3dcc121a9646415cebf; output-bytes=82; shell=/bin/sh; cwd=/Users/kiragu/Documents/crafting/jev-like-ai; path=ae60f164de85/21 entries

- [x] G18: desktop and 9:16 review captures exist, have valid dimensions, and the interface detector reports no high-severity findings
  CHECK: node scripts/verify_visual_review.mjs
  EXPECT: visual review verification passed
  EVIDENCE: automatic-evidence=v1; definition-sha256=5295cbba842560e6cf76fe6a28510aa98172f0b3466f368848a224d283028c8e; exit=0; EXPECT=matched; output-sha256=7b296251cdb0b7a88e6b1991b69a73148407c15d17c2771c96ae386d2067a723; output-bytes=34; shell=/bin/sh; cwd=/Users/kiragu/Documents/crafting/jev-like-ai; path=ae60f164de85/21 entries

- [x] G19: the README documents local development, offline replay, live Kev/SemIf operation, Docker isolation boundaries, and recording workflow
  CHECK: node scripts/verify_ai_bouncer_docs.mjs
  EXPECT: AI Bouncer documentation verification passed
  EVIDENCE: automatic-evidence=v1; definition-sha256=585494ae655ef4ad36142a5fac0dd91d33b3463ced31aa44aac7e112f260afad; exit=0; EXPECT=matched; output-sha256=41682df3e154f06ffe3c4b3abe1d426cc0815e6cacc7ebe059c88530ecf32198; output-bytes=45; shell=/bin/sh; cwd=/Users/kiragu/Documents/crafting/jev-like-ai; path=ae60f164de85/21 entries

- [x] G20: the original benchmark test suite still passes after the application integration
  CHECK: PYTHONPATH=src python3 scripts/run_tests.py
  EXPECT: benchmark unit tests passed
  EVIDENCE: automatic-evidence=v1; definition-sha256=5077d1f6e21c1cad28d56559dec7c67617edacd78a1a8a5d9eee8ba44024f828; exit=0; EXPECT=matched; output-sha256=78050ce0684f243fa5b4111ad142fa64db625108f533a057a4789e37f10297bf; output-bytes=2277; shell=/bin/sh; cwd=/Users/kiragu/Documents/crafting/jev-like-ai; path=ae60f164de85/21 entries
