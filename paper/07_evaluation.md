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
- `openclaw_ordered`: All modules, ordered execution with deterministic arbitration (our approach)

**Metrics.** For each scenario-strategy pair, we measure:
- **Accuracy:** Does the resolved verdict match the expected verdict?
- **Latency:** Wall-clock time per scenario (mean, median, P95 over 100 runs)
- **Conflict count:** Number of distinct non-ALLOW interventions
- **Trace completeness:** Can all module decisions be reconstructed, including explicit skip markers for short-circuited modules?

**Results.** Table 1 shows accuracy by strategy. OpenClaw-Ordered achieves 100% accuracy, correctly resolving all nine scenarios. Naive composition scores 1/9 (11.1%), failing on all scenarios except the negative control. Single-module strategies score 2–4/9 (22.2–44.4%), each catching only failures in their specific domain.

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
| **OpenClaw-Ordered** | **9/9** | **100.0%** |

**Latency overhead.** Table 2 reports latency measurements. OpenClaw-Ordered adds 0.0282ms mean overhead vs. no governance (+1762.5% relative, but +0.0282ms absolute). This absolute overhead is negligible compared to:
- LLM inference (100ms–10s per call)
- Network RTT for remote tool calls (10–1000ms)
- Human-in-the-loop escalation (seconds to minutes)

**Table 2: Latency by Strategy (real adapters, ms per scenario)**

| Strategy | Mean | Median | P95 | Absolute Overhead |
|----------|------|--------|-----|------------------|
| None (baseline) | 0.0016 | 0.0007 | 0.0052 | — |
| SARC Only | 0.0351 | 0.0222 | 0.0930 | +0.0335 |
| Authorization Only | 0.0086 | 0.0065 | 0.0153 | +0.0070 |
| Guardrail Only | 0.0049 | 0.0043 | 0.0064 | +0.0033 |
| ROMA Only | 0.0061 | 0.0055 | 0.0093 | +0.0045 |
| Async Only | 0.0060 | 0.0051 | 0.0084 | +0.0044 |
| Naive Composition | 0.0152 | 0.0120 | 0.0282 | +0.0136 |
| **OpenClaw-Ordered** | **0.0298** | **0.0252** | **0.0509** | **+0.0282** |

**Conflict resolution.** Only OpenClaw-Ordered correctly resolves Scenario 7 (`throttle_vs_serialize_conflict`), returning SERIALIZE (the stricter verdict) while recording both THROTTLE and SERIALIZE interventions in the trace. Scenario 8 (`audit_reconstruction`) returns DENY while preserving explicit skip markers for downstream modules, letting a reviewer reconstruct the full path from the unified trace. Naive composition returns ALLOW (short-circuits on first module's ALLOW), hiding the conflict entirely.

### 7.2 Governance Service Benchmark

**Methodology.** To validate composition at the model-call boundary, we implement a governance service exposing `check(action, ctx) → (verdict, trace)` over seven test cases covering PII leakage, toxicity, brand safety, regulatory compliance, and mixed conflicts.

**Results.** The service achieves:
- **Accuracy:** 7/7 (100%)
- **Detection rate:** 5/5 (100% of violations caught)
- **False positive rate:** 0/2 (0% false alarms)
- **P95 latency:** 0.0241ms
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

**Latency (real adapters):** Mean overhead is 0.0282ms—virtually identical to toy modules. This confirms that composition overhead is dominated by the resolution function, not individual module logic.

### 7.4 Threats to Validity

**Internal validity.** Our scenarios are handcrafted. While they cover diverse failure modes, they may not be exhaustive. Future work should mine real-world agent failure corpora to expand scenario coverage.

**External validity.** Evaluations use in-memory Python modules. Production deployments with networked guardrails, remote authz servers, and model inference will see higher absolute latencies (though relative overhead patterns should hold).

**Generalizability.** Results apply to systems with synchronous module execution and deterministic verdicts. Async governance (eventual consistency) or probabilistic enforcement (sampling-based auditing) are not evaluated.