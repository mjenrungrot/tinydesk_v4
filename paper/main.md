# LARE: A Linear, Verifier-Gated Framework for Autonomous Scientific Implementation Across Local and SLURM Environments

## Abstract
Autonomous research agents are increasingly used to assist with code generation and experimentation, but most systems still fail to provide deterministic execution, reproducible run tracking, and safe failure handling in real laboratory workflows. We present **LARE** (Linear Autonomous Research Engineer), a linear orchestration framework that couples agent-driven implementation with explicit state, staged verification, and environment-aware launch controls across local and SLURM settings. LARE introduces a mandatory **implementation review gate** between code changes and experiment launch, preventing unsafe or under-specified runs from entering expensive execution stages. The framework externalizes memory into a compact runtime state, structured iteration artifacts, and verifier outputs to ensure resumability and auditability. We define a practical design that supports end-to-end cycles from hypothesis to documentation with strict transition criteria and non-destructive failure policies. We further provide a reproducibility-oriented artifact contract (design specs, run manifests, metrics, analysis summaries, and paper updates) and an evaluation protocol that measures completion reliability, intervention rate, and rerun consistency. LARE is intended as a robust baseline for autonomous scientific implementation in resource-constrained and mixed local/cluster research environments.

## 1. Introduction
AI-assisted software development has improved the speed of prototyping and implementation in research. However, scientific workflows impose additional constraints beyond code synthesis: experiments must be reproducible, execution environments must be controlled, and results must be traceable to exact run metadata. In practice, many autonomous coding loops either rely on brittle completion signals or conflate planning, implementation, and launch without sufficient gating. This often leads to silent regressions, non-reproducible runs, or wasted compute allocation on shared clusters.

We address this gap with LARE, a linear orchestration framework designed for scientific implementation in two real execution contexts: local macOS development and remote SLURM compute nodes. LARE adopts three design commitments:

1. **Linear stage progression** with one active iteration and one active run at a time.
2. **Verifier-defined completion** instead of free-form model self-assertions.
3. **Durable external state** as the source of truth for resumability.

The key architectural contribution is a dedicated `IMPLEMENTATION_REVIEW` stage that sits between implementation and launch. This stage enforces launch readiness checks and routes failures back to implementation when issues are fixable, or to human review when retry budgets are exhausted. By inserting an explicit review gate, LARE reduces avoidable launch failures and improves operational safety for expensive runs.

## 2. Problem Formulation
Given a research objective and repository state, we seek an autonomous system that can repeatedly execute:

`hypothesis -> design -> implementation -> implementation_review -> launch -> extract_results -> update_docs -> decide_repeat`

while satisfying the following properties:

- **Correctness under staged contracts:** each stage has explicit required inputs, outputs, and verifiers.
- **Reproducibility:** all reported outcomes are backed by run manifests and artifact traces.
- **Resumability:** the loop can be interrupted and resumed using persisted state.
- **Safety:** destructive rollback is disallowed by default; failures transition to review states, not unchecked retries.

Let `S_t` denote the persisted runtime state at step `t`, and `V_t` the verifier outputs after stage execution. A transition is accepted only when the stage contract is satisfied:

`Accept_t = ContractSatisfied(S_t, V_t, Artifacts_t)`

The next state is produced deterministically by the finite-state transition function:

`S_{t+1} = T(S_t, decision_t, V_t)`

## 3. Method: LARE Architecture

### 3.1 Core Components
LARE is composed of:

- **Orchestrator:** executes exactly one stage transition per run command.
- **State store:** compact `state.json` with full readable keys.
- **Prompt registry:** stage-specific prompts with strict sectioned contracts.
- **Verifier suite:** environment, schema, run-health, and docs-target checks.
- **Execution adapters:** local command runner and SLURM submission/wait/sync handlers.

### 3.2 Compact State Model
LARE uses a compact but readable runtime state:

```json
{
  "iteration_id": "...",
  "stage": "implementation_review",
  "stage_attempt": 1,
  "last_run_id": "run_0003",
  "sync_status": "pending",
  "max_stage_attempts": 5,
  "max_total_iterations": 50
}
```

This design minimizes context payload while preserving interpretability.

### 3.3 Stage Contracts
Each stage defines:

- required inputs,
- required outputs,
- verifier criteria,
- transition policy on success/failure.

The `IMPLEMENTATION_REVIEW` stage is mandatory and produces:

- `implementation_review.md`
- `review_result.json` with status `pass|needs_retry|failed`

Launch is blocked unless review status is `pass`.

### 3.4 Local and SLURM Execution
LARE separates **control plane** and **execution plane**:

- Local repo is canonical control plane.
- Remote SLURM repo is execution mirror.

For SLURM runs, artifact repatriation back to local is required before result extraction. If remote-to-local sync fails, launch stage is marked retryable and extraction is blocked.

### 3.5 Verifier Policy Ladder
Verifier execution is policy-driven:

1. Run tests when configured/available.
2. Run required dry-run command.
3. Run canonical environment smoke check.

Completion is granted only when required checks pass (or are policy-allowed skips), and required artifacts exist.

## 4. Implementation
Our repository implementation includes:

- `.autolab/` scaffolding (state, prompts, schemas, policy, verifiers),
- iteration artifact scaffolding under `experiments/<ITERATION_ID>/`,
- structured prompts for all stages,
- a lightweight `src/target_product/` sample product implementation for framework-driven development tests.

The `src/target_product/` package intentionally stays simple:

- `domain.py`: product-domain entities and score normalization.
- `service.py`: a minimal ranking service with deterministic behavior.
- `evaluation.py`: summary metrics for ranked outputs.

This sample product exists to validate that the framework can iteratively develop a target application rather than framework internals.

## 5. Experimental Plan
We evaluate LARE in two tracks:

### 5.1 Operational Reliability
- Stage completion rate.
- Launch success rate (local and SLURM).
- Retry-to-human-review escalation frequency.
- Mean interventions per completed iteration.

### 5.2 Reproducibility Quality
- Manifest completeness rate.
- Rerun success from stored design + manifest.
- Artifact trace consistency (metrics, logs, figures).

### 5.3 Scientific Progress Metrics
- Improvement on primary task metric relative to baseline.
- Stability across seeds.
- Iteration efficiency (time and transitions to accepted results).

## 6. Baselines and Ablations
We compare LARE against:

1. **Single-shot agent implementation** (no staged loop).
2. **Loop without implementation review gate**.
3. **Loop with weak verifiers** (reduced required checks).

Ablations include:

- removing review stage,
- disabling sync-back blocking,
- replacing verifier-driven completion with token-only completion.

## 7. Safety and Failure Handling
LARE enforces:

- bounded stage retries,
- bounded total iterations,
- lock-based single-run exclusivity,
- non-destructive failure defaults.

When retries exceed budget, state transitions to `human_review`. Rollback is manual and commit-scoped (`git revert`) to avoid destructive workspace resets.

## 8. Discussion
The strongest practical effect of LARE is operational discipline: separating implementation from launch decisions avoids a common failure mode where generated code appears plausible but is not execution-safe. The compact state model reduces context overhead while remaining interpretable, and policy-driven verifiers provide flexibility for repositories with varying test maturity.

A current limitation is that verifier quality bounds system quality: weak checks can still permit poor transitions. Future work should integrate richer semantic checks and stronger artifact integrity validation.

## 9. Limitations
- The current implementation uses simple deterministic transition logic and does not yet include adaptive planning policies.
- Verifier scaffolds are placeholders and require project-specific implementations.
- The framework assumes a controlled local/SLURM split; broader multi-cluster topologies are future work.

## 10. Conclusion
LARE provides a practical framework for autonomous scientific implementation with explicit stage contracts, a mandatory implementation review gate, compact readable state, and deterministic verifier-driven transitions. By prioritizing reproducibility and safety, it offers a robust foundation for scaling autonomous experimentation in mixed local and SLURM research environments.

## References
- PaperBanana manuscript and prompts: `/Users/tjenrung/Workspaces/tinydesk_v4/paper/paperbanana.md`
- Ralph loop framing and persistence pattern: `/Users/tjenrung/Workspaces/tinydesk_v4/paper/ralph.md`
- Environment and orchestration design contracts: `/Users/tjenrung/Workspaces/tinydesk_v4/docs/environment.md`, `/Users/tjenrung/Workspaces/tinydesk_v4/docs/plan_automated_development.md`
