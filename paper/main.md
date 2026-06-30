# OpenClaw-Govern: Composable Runtime Governance for Recursive Tool-Using Agents

**Working title.** Replace with final title once contribution statement is tightened.

## Abstract

Multi-agent and tool-using AI systems are increasingly deployed in high-stakes domains, yet current governance approaches focus on single control mechanisms (constraints, guardrails, authorization) without addressing how these heterogenous modules compose at runtime. We present OpenClaw-Govern, a composable runtime governance layer for recursive tool-using/meta-agent systems. Our key contribution is not any individual control mechanism, but a composition architecture that defines: (1) ordered module execution with deterministic resolution semantics, (2) delegation-envelope propagation across authority boundaries, (3) conflict detection and arbitration among conflicting verdicts (ALLOW, DENY, THROTTLE, SERIALIZE, ESCALATE), and (4) unified trace trees that reconstruct governance decisions across modules. We formalize eight composition-specific failure modes and evaluate our approach against baseline strategies (single-module, naive composition, short-circuit evaluation). Our ordered composition strategy achieves 100% accuracy on all failure modes, while naive composition and single-module baselines fail on 5-7 of 8 scenarios. We position OpenClaw-Govern relative to SARC, runtime authorization overlays, path-based governance, telemetry architectures, and agent safety benchmarks (ToolEmu, τ-bench, AgentBench, HELM), showing that these works motivate but do not replace composition-specific governance evaluation.

## 1. Introduction

- Motivation: agents are no longer single-turn; they delegate, async-execute, and tool-use across trust boundaries.
- Problem: governance modules exist in isolation; composition is ad-hoc.
- Key insight: runtime governance must be composable with clear ordering, conflict resolution, and unified traces.
- Contributions:
  1. Composition architecture for heterogeneous governance modules.
  2. Formalization of 8 composition failure modes.
  3. Deterministic benchmark showing ordered composition vs. baselines.
  4. Positioning relative to related work.

## 2. Motivation: Composition Failures in the Wild

- Scenario 1: Budget overrun with delegated authority.
- Scenario 2: Delegation leak (child inherits permission but not parent constraints).
- Scenario 3: Stale authorization tokens.
- Scenario 4: Semantic guardrail bypass when modules short-circuit.
- Scenario 5: Async correlated-risk bypass.
- Scenario 6: Module conflict (THROTTLE vs SERIALIZE).
- Scenario 7: Audit reconstruction failure (fragmented traces).
- Scenario 8: Audit reconstruction (explicit skip markers).
- Scenario 9: Safe task (negative control).

## 3. System Model

- Agents, tools, actions.
- Governance modules: SARC-style constraints, authorization, ROMA-style delegation adapters, guardrails, async controllers.
- Verdict space: ALLOW, DENY, THROTTLE, SERIALIZE, ESCALATE.
- Delegation envelopes and scope attenuation.

## 4. Governance Module Interface

- Module signature: `module(action: Action, ctx: GovernanceContext) -> Decision`.
- Decision structure: `{module, verdict, reason, severity, trace_ref}`.
- Context propagation: what modules must share (delegation chains, cost caps, group risk, telemetry hooks).

## 5. Ordering and Conflict Semantics

- Ordered execution: why order matters (authz before budget before async).
- Resolution function: `resolve_ordered(decisions: List[Decision]) -> FinalVerdict`.
- Conflict detection: counting distinct non-ALLOW interventions.
- Arbitration rules: DENY > ESCALATE > SERIALIZE > THROTTLE > ALLOW.

## 6. Unified Trace Tree

- Trace reference construction: `delegation_chain:action_name`.
- Reconstructing full decision path from fragmented module traces.
- Tamper-evidence considerations (append-only logs, hashes).

## 7. Evaluation

See `experiments/composition_benchmark.py` and `experiments/governance_service_benchmark.py`.

- Benchmark design: 9 scenarios, 9 strategies.
- Metrics:
  - Final verdict accuracy.
  - Conflict count per scenario.
  - Intervention diversity.
  - Trace completeness (can we reconstruct the full path?).
  - Per-strategy latency overhead (mean/median/p95).
- Results:
  - `openclaw_ordered`: 9/9 accuracy.
  - `priority_composition`: 8/9 accuracy, still mis-resolves the `throttle` vs `serialize` conflict.
  - `naive_composition`: 1/9 (short-circuit failures).
  - Single-module baselines: 2-4/9 each.
- Latency overhead is now measured in the benchmark output and CSV export, so the remaining work is to interpret it in the paper rather than collect it.

## 8. Related Work

See `docs/related-work.md` for full matrix.

- SARC: runtime constraint enforcement.
- Authorization overlays: delegation and scope attenuation.
- Path-based governance: sequence-sensitive policy.
- Telemetry architectures: closed-loop enforcement.
- Robotics runtime governance: analogous patterns.
- Agent benchmarks (ToolEmu, τ-bench, AgentBench, HELM): evaluation lineage but not composition-specific.

## 9. Limitations

- Toy modules, not production SARC/Authz/AsyncFC.
- No real model inference in loop.
- Latency measurements preliminary.
- Single-agent focus; multi-agent coordination not yet evaluated.

## 10. Conclusion

- Composition is the missing layer.
- Ordered governance + unified traces enable deterministic runtime control.
- Future work: real adapters, latency benchmarks, multi-agent scenarios.

## References

- See `docs/related-work.md` for URLs.
- Will expand to BibTeX format for camera-ready.

---

## TODOs Before Submission

- [ ] Replace toy modules with real SARC/Authz/AsyncFC adapters (Issue #1).
- [ ] Add Governance Checks as a Service PoC endpoint example (Issue #4).
- [ ] Convert to LaTeX (or keep as MD for arXiv/SSRN).
- [ ] Add figures: architecture diagram and trace tree example.
- [ ] Tighten abstract and contribution statement based on reviewer feedback.