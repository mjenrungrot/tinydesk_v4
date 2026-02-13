# Plan: Autonomous Scientific Implementation (Linear Orchestrated Workflow + Implementation Review)

## 0. Purpose

We want a **reproducible, linear, agent-driven workflow** that can autonomously:

1. form a hypothesis,
2. design an experiment,
3. implement the necessary code and configs,
4. review the implementation for launch readiness,
5. launch the experiment (locally or on a SLURM compute node),
6. extract/aggregate results,
7. update documentation and paper artifacts,
8. repeat.

The end-goal is a **conference paper** describing the technique and empirically validating it.

This document defines a practical implementation plan for building this system as a **codebase** with:

- a durable orchestrator,
- explicit state memory,
- deterministic verifiers,
- safe failure behavior.

---

## 1. Constraints and non-negotiables

### 1.1 Execution locations
We develop and run on **exactly two locations**:

- **Local** development machine (macOS).
- **Remote** SLURM-managed compute node.

Both locations must use the **same environment contract** (`environment.yml` + `requirements-pip.txt`) and the same run interfaces.

### 1.2 End-goal: publishable research
The system is not just automation; it must be framed as a **technique** with:

- a clear problem definition,
- a method section (architecture + algorithms),
- evaluation protocol and baselines,
- ablations,
- limitations.

### 1.3 A codebase that automates experiment design + launch
The codebase must:

- generate/maintain experiment specifications,
- generate/modify code/configs,
- review implementation safety and scope,
- launch jobs reliably,
- capture results and metadata deterministically,
- surface artifacts that can be used in a paper.

### 1.4 Linear workflow only
No parallelization in orchestration:

- One active iteration at a time.
- One active experiment run at a time.
- No multi-branch or multi-agent concurrency.

Iterative refinement loops are allowed only when they are sequential.

### 1.5 Canonical loop
We explicitly commit to this linear loop:

`[hypothesis] -> [experiment design] -> [implementation] -> [implementation review] -> [launch experiment] -> [extract results] -> [update documentation] -> [repeat]`

The orchestrator must encode this loop as a state machine.

---

## 2. Inspirations to combine: PaperBanana + Ralph

This system combines patterns from `/Users/tjenrung/Workspaces/tinydesk_v4/paper/paperbanana.md` and `/Users/tjenrung/Workspaces/tinydesk_v4/paper/ralph.md`.

### 2.1 Ralph contributes the outer execution loop + state persistence
Ralph emphasizes:

- stable outer loop,
- explicit completion predicate,
- persistent external state,
- bounded retries + manual stop.

We reuse:

- recoverability from disk state,
- verifier-defined completion (not model self-claims),
- deterministic progress logs.

### 2.2 PaperBanana contributes modular roles + plan/refine decomposition
PaperBanana demonstrates:

- linear planning phases,
- iterative critique/refinement loops,
- role-specific prompt contracts.

We reuse:

- role contracts per stage,
- staged refinement,
- critique before launch.

### 2.3 Combined principle
We implement:

- Ralph-style outer loop for full workflow,
- PaperBanana-style review/critique as an explicit stage (`IMPLEMENTATION_REVIEW`).

---

## 3. Proposed system: Linear Autonomous Research Engineer

Working name: **LARE** (*Linear Autonomous Research Engineer*).

### 3.1 Core components

1. **Orchestrator**
   - Runs the linear FSM.
   - Selects next stage.
   - Builds prompt bundles.
   - Invokes configurable agent runner.
   - Runs verifiers.
   - Persists state transitions.

2. **State store (durable memory)**
   - File-based state under `.autolab/` and `experiments/`.
   - Structured logs and manifests.

3. **Prompt registry**
   - Stage templates in `.autolab/prompts/`.

4. **Verifier suite**
   - Environment, schema, dry-run, results sanity, docs target checks.

5. **Execution adapters**
   - Local runner.
   - SLURM runner with sync-aware artifact collection.

### 3.2 Iteration abstraction
One iteration includes:

- hypothesis -> design -> implementation -> implementation review -> run -> analysis -> docs.

Each iteration ends with a decision:

- continue,
- refine,
- stop,
- or transition to `HUMAN_REVIEW`.

---

## 4. Repository layout conventions

### 4.1 Target directory structure

```text
.
├── .autolab/
│   ├── state.json
│   ├── backlog.yaml
│   ├── lock
│   ├── verifier_policy.yaml
│   ├── logs/
│   │   ├── orchestrator.log
│   │   └── iterations/
│   ├── prompts/
│   │   ├── stage_hypothesis.md
│   │   ├── stage_design.md
│   │   ├── stage_implementation.md
│   │   ├── stage_implementation_review.md
│   │   ├── stage_launch.md
│   │   ├── stage_extract.md
│   │   ├── stage_docs.md
│   │   └── shared/
│   ├── schemas/
│   │   ├── design.schema.json
│   │   └── agent_result.schema.json
│   └── verifiers/
│       ├── schema_checks.py
│       ├── result_sanity.py
│       ├── docs_targets.py
│       └── run_health.py
├── experiments/
│   └── <ITERATION_ID>/
│       ├── hypothesis.md
│       ├── design.yaml
│       ├── implementation_plan.md
│       ├── implementation_review.md
│       ├── review_result.json
│       ├── launch/
│       │   ├── run_local.sh
│       │   └── run_slurm.sbatch
│       ├── runs/
│       │   └── <RUN_ID>/
│       │       ├── run_manifest.json
│       │       ├── logs/
│       │       ├── metrics.json
│       │       └── artifacts/
│       ├── analysis/
│       │   ├── summary.md
│       │   ├── tables/
│       │   └── figures/
│       └── docs_update.md
├── paper/
│   ├── paperbanana.md
│   ├── ralph.md
│   └── figures/
└── docs/
    ├── environment.md
    ├── design/repository_environment.md
    └── plan_automated_development.md
```

Notes:

- `.autolab/` stores orchestration control-plane state.
- `experiments/<ITERATION_ID>/` stores iteration-local truth.
- Existing paper files are preserved; no forced rename/migration in MVP.

### 4.2 Git policy
Commit:

- experiment specs,
- run manifests and aggregate metrics,
- analysis summaries,
- paper text + final figures,
- verifier and prompt contracts.

Do not commit by default:

- large checkpoints,
- large raw logs,
- datasets.

---

## 5. Environment contract (local + SLURM)

`/Users/tjenrung/Workspaces/tinydesk_v4/docs/environment.md` is the runtime contract.

### 5.1 Shared baseline

- Python `3.13`
- pinned torch stack
- environment from `environment.yml` + `requirements-pip.txt`
- bootstrap via `scripts/bootstrap_venv.sh`

### 5.2 Command discipline
Use explicit binaries:

- `./venv/bin/python`
- `./venv/bin/pip`

### 5.3 Canonical smoke verifier
Canonical command:

```bash
./venv/bin/python -c "import torch, torchvision, torchaudio, numpy, matplotlib, lightning; print('tinydesk_v4 env ready')"
```

Verifier semantics:

- **Pass:** exit code `0`.
- **Fail:** non-zero exit code.
- Output text can be logged but must not be sole pass/fail signal.

### 5.4 Remote SLURM prerequisites

- `squeue` and `sinfo` available on launch node/session.
- remote checkout under approved paths.
- cache directories on node-local disk when available.

---

## 6. State model and persistence

### 6.1 Durable state principle
True memory = filesystem + git + state files + append-only logs.

No critical control data may live only in model context.

### 6.2 Global orchestrator state
File: `.autolab/state.json`

```json
{
  "iteration_id": "2026-02-12T23-30-00Z_h1",
  "stage": "implementation_review",
  "stage_attempt": 1,
  "last_run_id": "run_0003",
  "sync_status": "pending",
  "max_stage_attempts": 5,
  "max_total_iterations": 50
}
```

Compact full-key map:

- `iteration_id`: active iteration id
- `stage`: active workflow stage
- `stage_attempt`: retry counter for current stage
- `last_run_id`: most recent run id
- `sync_status`: sync status (`pending|ok|failed|na`)
- `max_stage_attempts`: stage retry budget
- `max_total_iterations`: global loop budget

`stage` enum values:

- `hypothesis`
- `design`
- `implementation`
- `implementation_review`
- `launch`
- `extract_results`
- `update_docs`
- `decide_repeat`
- `human_review`
- `stop`

### 6.3 Iteration-local state
Each `experiments/<ITERATION_ID>/` contains:

- `hypothesis.md`
- `design.yaml`
- `implementation_plan.md`
- `implementation_review.md`
- `review_result.json`
- `runs/<RUN_ID>/run_manifest.json`
- `analysis/summary.md`
- `docs_update.md`

### 6.4 Backlog model
File: `.autolab/backlog.yaml`

```yaml
hypotheses:
  - id: h1
    status: open
    title: "Augmentation X improves metric Y"
    success_metric: "val_accuracy"
    target_delta: 0.02
experiments:
  - id: e1
    hypothesis_id: h1
    status: in_progress
    iteration_id: 2026-02-12T23-30-00Z_h1
```

---

## 7. Linear workflow as a state machine

FSM:

```text
HYPOTHESIS
  -> DESIGN
  -> IMPLEMENTATION
  -> IMPLEMENTATION_REVIEW
     -> (LAUNCH | IMPLEMENTATION)
  -> LAUNCH
  -> EXTRACT_RESULTS
  -> UPDATE_DOCS
  -> DECIDE_REPEAT
     -> (HYPOTHESIS | DESIGN | STOP)
```

Key requirements:

- exactly one active state,
- explicit required inputs/outputs/verifiers per stage,
- explicit retry budget per stage.

Failure handling:

- each stage retries up to `state.max_stage_attempts`,
- on exhaustion: write failure report and transition to `HUMAN_REVIEW`.

Non-destructive policy:

- no automatic workspace reset,
- no automatic `git reset --hard`,
- optional rollback is manual and commit-scoped (`git revert` on orchestrator-owned commits only).

---

## 8. Stage-by-stage contracts

### 8.1 Stage: Hypothesis

**Goal**: produce a testable hypothesis with measurable success criteria.

**Outputs**:

- `hypothesis.md` with metric, expected delta, success definition, and risk bounds.

**Verifier**:

- file exists,
- required fields present.

### 8.2 Stage: Design

**Goal**: convert hypothesis into executable spec.

**Outputs**:

- `design.yaml` with dataset, config changes, compute plan, seeds, baselines, aggregation.

**Verifier**:

- schema validation,
- required fields,
- entrypoint references exist or are explicitly planned.

### 8.3 Stage: Implementation

**Goal**: make design runnable.

**Outputs**:

- code/config diffs,
- `implementation_plan.md` updated,
- verifier output artifacts (test/dry-run logs).

**Verifier policy ladder** (from `.autolab/verifier_policy.yaml`):

1. If `test_command` is configured and tests exist:
   - run tests and enforce pass when `require_tests: true`.
2. Run dry-run command when configured:
   - enforce pass when `require_dry_run: true`.
3. Always run environment smoke verifier.

Unconditional `pytest` is **not** required for MVP.

### 8.4 Stage: Implementation review

**Goal**: verify implementation is launch-safe, scope-compliant, and reproducible before job submission.

**Required inputs**:

- `design.yaml`
- implementation diff
- verifier outputs
- dry-run output
- current state snapshot

**Required outputs**:

- `implementation_review.md`
- `review_result.json`
- reviewer feedback log (in iteration logs)

**Pass criteria**:

- required checks pass,
- configured review checks pass,
- no blocking findings.

**Transitions**:

- `pass` -> `LAUNCH`
- `needs_retry` -> `IMPLEMENTATION`
- exhausted retries -> `HUMAN_REVIEW`

**Launch gate**:

`LAUNCH` is forbidden unless `review_result.json.status == "pass"`.

### 8.5 Stage: Launch

**Goal**: run experiment from approved implementation.

**Supported modes**:

- local launch,
- SLURM launch.

**Required sub-steps**:

1. `sync_to_remote` (for SLURM mode)
2. `submit`
3. `wait`
4. `collect_to_remote`
5. `sync_artifacts_to_local`
6. `verify_local_artifacts`

**Outputs**:

- launch scripts under `launch/`
- `runs/<RUN_ID>/run_manifest.json`
- run logs

**Verifier**:

- local: exit code `0` + expected artifacts,
- SLURM: completed job + successful artifact repatriation to local control plane.

**Retry behavior**:

- if `sync_artifacts_to_local` fails, stage returns `needs_retry` and cannot transition to `EXTRACT_RESULTS`.

### 8.6 Stage: Extract results

**Goal**: produce structured analysis outputs.

**Outputs**:

- `metrics.json`
- `analysis/summary.md`
- `analysis/tables/*.csv`
- `analysis/figures/*.png|.pdf`

**Verifier**:

- valid metrics JSON,
- primary metric present,
- plots generated successfully.

### 8.7 Stage: Update documentation

**Goal**: persist outcomes in project docs and paper files.

**Outputs**:

- `docs_update.md`
- updates to:
  - `paper/paperbanana.md` (method/experiments updates),
  - `paper/ralph.md` (loop/reliability updates when relevant),
  - `paper/figures/`.

**Verifier**:

- mapped paper targets updated, or explicit "no changes needed" rationale recorded.

### 8.8 Stage: Decide repeat

**Goal**: choose next step.

Possible decisions:

- refine same hypothesis,
- start new hypothesis,
- stop,
- escalate to human review.

Decision rationale must be recorded in `analysis/summary.md`.

---

## 9. Orchestrator design

### 9.1 CLI

- `./venv/bin/python -m autolab init`
  - create `.autolab/` scaffolding and default contracts.

- `./venv/bin/python -m autolab run`
  - execute one stage transition.

- `./venv/bin/python -m autolab loop --max-iterations N`
  - sequential loop with hard caps.

- `./venv/bin/python -m autolab status`
  - print current stage and sync status.

### 9.2 Loop semantics

```text
while not STOP:
  load state.json
  run current stage handler
  run stage verifiers
  if stage complete:
    transition
  elif attempts remain:
    retry
  else:
    transition to HUMAN_REVIEW
```

### 9.3 Stage handler result

```json
{
  "status": "complete | needs_retry | failed",
  "artifacts": {},
  "feedback": "..."
}
```

### 9.4 Agent runner interface (mandatory structured result)

Agent execution must output `.autolab/agent_result.json`.

Required schema:

```json
{
  "status": "complete | needs_retry | failed",
  "summary": "string",
  "changed_files": ["path/to/file"],
  "completion_token_seen": true
}
```

Rules:

- missing or invalid `agent_result.json` => `needs_retry`.
- completion token is optional observability; token presence alone is never completion.

### 9.5 Prompt registry

Prompts live under `.autolab/prompts/` and are versioned.

### 9.6 Completion policy

Stage completion requires **verifier success** plus valid stage artifacts.

Completion token is a secondary signal only.

---

## 10. Local vs remote execution model

### 10.1 Control plane vs execution plane

- **Local repo is canonical control plane**.
- **Remote repo is execution mirror**.

State transitions are committed against local control plane state.

### 10.2 Sync contract (required)

Code sync:

- local -> remote via git (required).

Artifact sync:

- remote -> local via rsync/scp (required for SLURM runs).

### 10.3 Blocking repatriation rule

`EXTRACT_RESULTS` cannot start until:

- remote artifacts are copied back,
- local artifact presence checks pass,
- `state.sync_status == "ok"`.

### 10.4 SLURM runner responsibilities

- `submit(sbatch_script) -> job_id`
- `wait(job_id)` using `squeue/sacct`
- `collect(job_id)` to remote run directory
- `sync_back(run_id)` to local control plane

All metadata is recorded in `run_manifest.json`.

---

## 11. Verification suite and policy ladder

### 11.1 Verifier config file
File: `.autolab/verifier_policy.yaml`

Controls:

- test command
- dry-run command
- required/optional gates
- docs target checks

### 11.2 Environment verifier

- canonical smoke command (Section 5.3)
- python version check

### 11.3 Implementation verifiers

- optional tests (policy-driven)
- required dry-run when configured
- schema checks

### 11.4 Review verifiers

- review artifact presence (`implementation_review.md`, `review_result.json`)
- no blocking findings
- required checks set to pass/skip according to policy

### 11.5 Run completion verifiers

- run completion status
- expected artifacts
- sync-back success for remote runs

### 11.6 Results sanity verifiers

- valid metric ranges
- no NaNs
- expected seed aggregation
- baseline included

---

## 12. Paper production integration

### 12.1 Default paper targets
MVP defaults:

- `paper/paperbanana.md`
- `paper/ralph.md`
- `paper/figures/`

No forced migration to `paper/method.md` or `paper/experiments.md`.

### 12.2 Minimum generated assets

- results table in `analysis/tables/`
- key plots in `analysis/figures/`
- method/system figure in `paper/figures/`

---

## 13. Conference paper evaluation plan

### 13.1 Research questions

- Does linear staged orchestration outperform single-shot coding?
- Which components contribute most (review gate, verifiers, retrieval, critique)?
- How robust is local + remote execution reproducibility?

### 13.2 Baselines

- single-shot agent baseline
- outer-loop-only baseline
- decomposition without review stage
- decomposition without retrieval

### 13.3 Metrics

Operational:

- completion success rate
- iterations/time to completion
- number of human interventions
- rerun reproducibility from manifest

Scientific:

- primary benchmark improvement
- cross-seed stability

### 13.4 Ablations

- remove implementation review stage
- weaken verifier policy
- remove structured state store

### 13.5 Credibility checklist

- every result tied to manifest
- manifest has commit + command + env + sync status
- tables/plots generated by committed scripts

---

## 14. Safety and guardrails

Enforced controls:

- max attempts per stage
- max total iterations
- manual abort support
- lock file to prevent concurrent loops
- non-destructive default failure handling

Forbidden by default:

- destructive git resets
- automatic deletion of unrelated workspace files

Allowed rollback path:

- human-approved, commit-scoped `git revert` only.

---

## 15. Development milestones (ordered, linear)

### Milestone A: Scaffolding

- initialize `.autolab/` structure,
- create policy, schema, prompt, verifier placeholders.

### Milestone B: FSM skeleton

- implement state model with `implementation_review` stage,
- implement dry transition runner.

### Milestone C: Implementation review gate

- implement `IMPLEMENTATION_REVIEW` stage contract,
- enforce launch gate and back-edge to `IMPLEMENTATION`.

### Milestone D: Launch + sync

- implement local/SLURM launch adapters,
- enforce sync-back blocking before extraction.

### Milestone E: Verifier ladder

- implement policy-driven tests/dry-run/smoke checks,
- implement review and docs-target verifiers.

### Milestone F: Agent integration

- enforce `.autolab/agent_result.json` interface,
- treat malformed output as retryable failure.

### Milestone G: End-to-end toy iteration

- run one full iteration,
- verify all stage outputs and docs updates.

### Milestone H: Research-scale evaluation

- run multi-iteration study,
- collect reliability and scientific metrics.

---

## 16. Operational acceptance matrix

The system is accepted when all scenarios pass:

1. implementation passes initial checks, review finds blocking issue, flow returns to `IMPLEMENTATION`.
2. remote job completes but sync-back fails, flow stays in `LAUNCH` and does not advance.
3. repository without tests succeeds via policy fallback (dry-run + smoke).
4. malformed `.autolab/agent_result.json` results in `needs_retry` with logged failure.
5. retry budget exhausted in review stage transitions to `HUMAN_REVIEW` with no destructive rollback.
6. docs updates write to existing paper targets (`paper/paperbanana.md`, `paper/ralph.md`).
7. interrupted loop resumes from persisted state without duplicate submission.

---

## Appendix A: Example `design.yaml` (minimal)

```yaml
id: e1
iteration_id: 2026-02-12T23-30-00Z_h1
hypothesis_id: h1

description: |
  Evaluate whether augmentation X improves metric Y.

entrypoint:
  module: tinydesk_v4.train
  args:
    config: experiments/<ITERATION_ID>/design.yaml

compute:
  location: slurm  # local|slurm
  slurm:
    partition: default
    time: "08:00:00"
    cpus_per_task: 8
    mem_gb: 64
    gpus: 1

reproducibility:
  seeds: [0, 1, 2]
  deterministic: true

metrics:
  primary: val_accuracy
  secondary: [train_loss]
  success_delta: 0.02

baselines:
  - name: baseline_current
    config_overrides: {}

variants:
  - name: aug_x_on
    config_overrides:
      augmentation_x: true
```

---

## Appendix B: Example `run_manifest.json` (minimal)

```json
{
  "run_id": "run_0003",
  "iteration_id": "2026-02-12T23-30-00Z_h1",
  "git": {
    "control_plane_commit": "<hash>",
    "remote_commit": "<hash>",
    "dirty": false
  },
  "location": "slurm",
  "slurm": {
    "job_id": "123456",
    "partition": "default",
    "time": "08:00:00",
    "cpus": 8,
    "mem_gb": 64,
    "gpus": 1
  },
  "command": "./venv/bin/python -m tinydesk_v4.train --config experiments/.../design.yaml",
  "sync": {
    "artifact_sync_to_local": {
      "status": "ok",
      "completed_at": "..."
    }
  },
  "verifier_results": {
    "env_smoke": "pass",
    "tests": "skip",
    "dry_run": "pass"
  },
  "started_at": "...",
  "ended_at": "...",
  "artifacts": {
    "stdout": "runs/run_0003/logs/stdout.txt",
    "stderr": "runs/run_0003/logs/stderr.txt",
    "metrics": "runs/run_0003/metrics.json"
  }
}
```

---

## Appendix C: Example `review_result.json` schema

```json
{
  "status": "pass|needs_retry|failed",
  "blocking_findings": [],
  "required_checks": {
    "tests": "pass|skip|fail",
    "dry_run": "pass|fail",
    "schema": "pass|fail"
  },
  "reviewed_at": "ISO-8601"
}
```

---

## Appendix D: Example `.autolab/verifier_policy.yaml`

```yaml
test_command: "./venv/bin/python -m pytest"
dry_run_command: "./venv/bin/python -m tinydesk_v4.train --config experiments/<ITERATION_ID>/design.yaml --dry-run"
require_tests: false
require_dry_run: true
require_env_smoke: true
require_docs_target_update: true
```

---

## Appendix E: Prompt template skeletons

### E.1 `stage_implementation_review.md`

```markdown
# ROLE
You are the Implementation Reviewer.

# INPUTS
- design.yaml: {{design_yaml}}
- implementation diff: {{diff_summary}}
- verifier outputs: {{verifier_outputs}}
- dry-run output: {{dry_run_output}}
- state snapshot: {{state_json}}

# TASK
Produce:
- experiments/{{iteration_id}}/implementation_review.md
- experiments/{{iteration_id}}/review_result.json

Rules:
- Block launch when scope/regression/reproducibility risks are unresolved.
- Return `needs_retry` when fixes belong to implementation.
- Return `failed` only for non-recoverable conditions.

# DONE WHEN
- review artifacts exist and validate.
- all required checks pass.
```

### E.2 `stage_implementation.md`

```markdown
# ROLE
You are the Research Engineer.

# INPUTS
- design.yaml: {{design_yaml}}
- review feedback (if retry): {{review_feedback}}
- verifier errors: {{verifier_errors}}

# TASK
Implement required code/config changes with minimal diffs.

# DONE WHEN
- required verifier policy checks pass
- review handoff bundle is complete
```
