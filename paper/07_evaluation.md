## 7. Evaluation

We evaluate OpenClaw-Govern along three dimensions: **composition correctness** (does ordered composition resolve all failure modes?), **latency overhead** (what is the runtime cost?), and **generalizability** (do results hold with real governance adapters, not just toy modules?).

### 7.1 Composition Benchmark

**Methodology.** We construct nine deterministic scenarios covering the failure modes from Section 2.4:

1. `budget_overrun` — Action exceeds SARC-style budget cap (expected: DENY)
2. `delegation_leak` — Agent attempts write outside delegated read scope (expected: DENY)
3. `stale_auth` — Expired authorization token (expected: DENY)
4. `semantic_risk` — High-risk semantic guardrail violation (expected: DENY)
5. `async_correlated_risk` — Concurrent actions exceed correlated risk threshold (expected: SERIALIZE)
6. `delegated_budget_inheritance` — Parent budget cap inherited via ROMA delegation (expected: DENY)
7. `throttle_vs_serialize_conflict` — Conflicting THROTTLE and SERIALIZE verdicts (expected: SERIALIZE)
8. `audit_reconstruction` — Short-circuited denial with explicit skip markers (expected: DENY)
9. `safe_task` — Negative control, benign action (expected: ALLOW)

We evaluate nine strategies:
- `none`: No governance (baseline)
- Single-module strategies: `sarc_only`, `authz_only`, `guardrail_only`, `roma_only`, `async_only`
- `naive_composition`: All modules, first-ALLOW short-circuit (fragmented composition)
- `priority_composition`: All modules, priority-ranked arbitration without severity-aware conflict resolution
- `openclaw_ordered`: All modules, ordered execution with deterministic arbitration (our approach)

**Metrics.** For each scenario-strategy pair, we measure:
- **Accuracy:** Does the resolved verdict match the expected verdict?
- **Latency:** Wall-clock time per scenario (single deterministic pass; summarized as mean, median, P95 across the nine scenarios)
- **Conflict count:** Number of distinct non-ALLOW interventions
- **Trace completeness:** Can all module decisions be reconstructed, including explicit skip markers for short-circuited modules in the toy benchmark export?

**Results.** Table 1 shows accuracy by strategy. OpenClaw-Ordered achieves 100% accuracy, correctly resolving all nine scenarios. Priority composition is a stronger baseline than naive short-circuiting, but it still mis-resolves Scenario 7 and therefore scores 8/9. Naive composition scores 1/9 (11.1%), failing on all scenarios except the negative control. Single-module strategies score 2–4/9 (22.2–44.4%), each catching only failures in their specific domain.

**Table 1: Accuracy by Strategy (9 scenarios)**

| Strategy | Accuracy | % Correct |
|----------|----------|-----------|
| None (baseline) | 1/9 | 11.1% |
| SARC Only | 2/9 | 22.2% |
| Authorization Only | 4/9 | 44.4% |
| Guardrail Only | 2/9 | 22.2% |
| ROMA Only | 2/9 | 22.2% |
| Async Only | 3/9 | 33.3% |
| Naive Composition | 1/9 | 11.1% |
| Priority Composition | 8/9 | 88.9% |
| **OpenClaw-Ordered** | **9/9** | **100.0%** |

**Latency overhead.** Table 2 reports latency measurements from the current real-adapter benchmark run. OpenClaw-Ordered adds 0.0050ms mean overhead vs. no governance (+1000% relative, but still sub-0.01ms absolute). This absolute overhead is negligible compared to:
- LLM inference (100ms–10s per call)
- Network RTT for remote tool calls (10–1000ms)
- Human-in-the-loop escalation (seconds to minutes)

**Table 2: Latency by Strategy (real adapters, ms per scenario)**

| Strategy | Mean | Median | P95 | Absolute Overhead |
|----------|------|--------|-----|------------------|
| None (baseline) | 0.0005 | 0.0003 | 0.0017 | — |
| SARC Only | 0.0059 | 0.0050 | 0.0124 | +0.0054 |
| Authorization Only | 0.0018 | 0.0015 | 0.0031 | +0.0013 |
| Guardrail Only | 0.0011 | 0.0010 | 0.0016 | +0.0006 |
| ROMA Only | 0.0011 | 0.0010 | 0.0016 | +0.0006 |
| Async Only | 0.0014 | 0.0011 | 0.0025 | +0.0009 |
| Naive Composition | 0.0029 | 0.0022 | 0.0058 | +0.0024 |
| **OpenClaw-Ordered** | **0.0055** | **0.0049** | **0.0084** | **+0.0050** |

**Conflict resolution.** Only OpenClaw-Ordered correctly resolves Scenario 7 (`throttle_vs_serialize_conflict`), returning SERIALIZE (the stricter verdict) while recording both THROTTLE and SERIALIZE interventions in the toy benchmark trace export. Scenario 8 (`audit_reconstruction`) returns DENY while preserving explicit skip markers in the toy benchmark when `audit_trace=True`; the real-adapter validation currently checks verdict correctness and trace completeness, but does not export skip markers. Naive composition returns ALLOW (short-circuits on first module's ALLOW), hiding the conflict entirely.

### 7.2 Governance Service Benchmark

**Methodology.** To validate composition at the model-call boundary, we implement a governance service exposing `check(action, ctx) → (verdict, trace)` over seven test cases covering PII leakage, toxicity, brand safety, regulatory compliance, and mixed conflicts.

**Results.** The service achieves:
- **Accuracy:** 7/7 (100%)
- **Detection rate:** 5/5 (100% of violations caught)
- **False positive rate:** 0/2 (0% false alarms)
- **P95 latency:** 0.0182ms
- **Trace completeness:** 7/7 (100%)

In the `mixed_conflict` case (simultaneous PII + brand safety + regulatory violations), the service correctly returns DENY while recording all three interventions (DENY, ESCALATE, REWRITE) in the unified trace.

### 7.3 Real Adapter Validation

**Motivation.** Sections 7.1 and 7.2 use deterministic toy functions. To demonstrate generalizability, we replace toy modules with thin adapters around real implementations:
- SARC: `sarc.spec.ConstraintSpec` + `sarc.enforcement.PreActionGate` [1]
- AuthZ: `authz.propagation.AuthorizationPropagator` [2]
- AsyncFC: `asyncfc_sarc.governed_future.GovernedFutureOrchestrator` [8]
- ROMA: Custom adapter with inherited cost caps
- Guardrail: Semantic risk classifier

**Results.** Table 3 compares toy vs. real adapter accuracy. Results are identical—OpenClaw-Ordered achieves 9/9 with real adapters, demonstrating the composition semantics generalize beyond toy functions.

**Table 3: Toy vs. Real Adapter Accuracy**

| Strategy | Toy Modules | Real Adapters |
|----------|-------------|---------------|
| OpenClaw-Ordered | 9/9 (100%) | 9/9 (100%) |
| Naive Composition | 1/9 (11.1%) | 1/9 (11.1%) |
| SARC Only | 2/9 (22.2%) | 2/9 (22.2%) |
| AuthZ Only | 4/9 (44.4%) | 4/9 (44.4%) |

**Latency (real adapters):** Mean overhead is 0.0055ms with P95 at 0.0084ms—virtually identical to the toy benchmark's sub-0.01ms regime. This confirms that composition overhead is dominated by the resolution function and adapter plumbing, not individual module logic.

### 7.4 Threats to Validity

**Internal validity.** Our scenarios are handcrafted. While they cover diverse failure modes, they may not be exhaustive. Future work should mine real-world agent failure corpora to expand scenario coverage.

**External validity.** Evaluations use in-memory Python modules. Production deployments with networked guardrails, remote authz servers, and model inference will see higher absolute latencies (though relative overhead patterns should hold).

**Generalizability.** Results apply to systems with synchronous module execution and deterministic verdicts. Async governance (eventual consistency) or probabilistic enforcement (sampling-based auditing) are not evaluated.
