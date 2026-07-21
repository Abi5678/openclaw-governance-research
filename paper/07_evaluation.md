## 7. Evaluation

We evaluate OpenClaw-Govern along three dimensions: **composition correctness** (does ordered composition resolve all failure modes?), **latency overhead** (what is the runtime cost?), and **generalizability** (do results hold with real governance adapters, not just toy modules?).

### 7.1 Composition Benchmark

**Methodology.** We construct eleven deterministic scenarios covering the failure modes from Section 2.4:

1. `budget_overrun` — SARC-style cost limit enforcement (expected: DENY)
2. `delegation_leak` — write outside delegated read scope (expected: DENY)
3. `stale_auth` — expired authorization token (expected: DENY)
4. `semantic_risk` — guardrail violation on high-risk action (expected: DENY)
5. `async_correlated_risk` — correlated async actions requiring serialization (expected: SERIALIZE)
6. `delegated_budget_inheritance` — parent cost cap inherited through delegation chain (expected: DENY)
7. `throttle_vs_serialize_conflict` — conflict between THROTTLE and SERIALIZE verdicts (expected: SERIALIZE)
8. `audit_reconstruction` — short-circuited denial with explicit skip markers (expected: DENY)
9. `delegated_remediation_conflict` — ROMA-style delegation lineage plus AARM-style interception plus async serialization/conflict arbitration (expected: ESCALATE)
10. `policy_laundering` — sanitized summary with preserved unsafe provenance across the adapter boundary (expected: DENY)
11. `safe_task` — negative control, benign action (expected: ALLOW)

The current benchmark snapshot now includes eleven scenarios. The `policy_laundering` case is scored separately on provenance retention, so the reported counts below include both verdict accuracy and whether the original unsafe request survived sanitization across the adapter / summary boundary.

We evaluate nine strategies:
- `none`: No governance (baseline)
- Single-module strategies: `sarc_only`, `authz_only`, `guardrail_only`, `roma_only`, `async_only`
- `naive_composition`: All modules, first-ALLOW short-circuit (fragmented composition)
- `priority_composition`: All modules, priority-ranked arbitration without severity-aware conflict resolution
- `openclaw_ordered`: All modules, ordered execution with deterministic arbitration (our approach)

**Metrics.** For each scenario-strategy pair, we measure:
- **Accuracy:** Does the resolved verdict match the expected verdict?
- **Latency:** Wall-clock time per scenario (single deterministic pass; summarized as mean, median, P95 across the eleven scenarios)
- **Conflict count:** Number of distinct non-ALLOW interventions
- **Trace completeness:** Can all module decisions be reconstructed, including explicit skip markers for short-circuited modules in the toy benchmark export, provenance through any sanitizing adapter or summary step, and, for `delegated_remediation_conflict`, both the delegation lineage and the step-up/serialization interventions?
- **Provenance retention:** The `policy_laundering` scenario scores whether the original unsafe request survives the adapter / summary boundary, even when the intermediate text is sanitized. This is evaluated separately from verdict accuracy so the laundering case measures lineage recovery without recentering the benchmark on prompt-injection defense.

**Results.** Table 1 shows accuracy by strategy. OpenClaw-Ordered achieves 100% accuracy, correctly resolving all eleven scenarios. Priority composition is a stronger baseline than naive short-circuiting, but it still mis-resolves the conflict cases and therefore trails the ordered stack. Naive composition scores 1/11 (9.1%), failing on all scenarios except the negative control. Single-module strategies score 2–5/11 (18.2–45.5%), each catching only failures in their specific domain.

**Table 1: Accuracy by Strategy (11 scenarios)**

| Strategy | Accuracy | % Correct |
|----------|----------|-----------|
| None (baseline) | 1/11 | 9.1% |
| SARC Only | 2/11 | 18.2% |
| Authorization Only | 5/11 | 45.5% |
| Guardrail Only | 3/11 | 27.3% |
| ROMA Only | 2/11 | 18.2% |
| Async Only | 3/11 | 27.3% |
| Naive Composition | 1/11 | 9.1% |
| Priority Composition | 10/11 | 90.9% |
| **OpenClaw-Ordered** | **11/11** | **100.0%** |

**Latency overhead.** Table 2 reports latency measurements from the current real-adapter benchmark snapshot in `results/composition_benchmark_real_adapters.csv`. OpenClaw-Ordered adds 0.1824ms mean overhead vs. no governance in the current adapter-backed run. That remains small relative to:
- LLM inference (100ms–10s per call)
- Network RTT for remote tool calls (10–1000ms)
- Human-in-the-loop escalation (seconds to minutes)

**Table 2: Latency by Strategy (real adapters, ms per scenario)**

| Strategy | Mean | Median | P95 | Absolute Overhead |
|----------|------|--------|-----|------------------|
| None (baseline) | 0.0013 | 0.0008 | 0.0034 | — |
| SARC Only | 0.0190 | 0.0118 | 0.0449 | +0.0177 |
| Authorization Only | 0.0134 | 0.0058 | 0.0478 | +0.0121 |
| Guardrail Only | 0.0050 | 0.0040 | 0.0089 | +0.0037 |
| ROMA Only | 0.0039 | 0.0033 | 0.0056 | +0.0026 |
| Async Only | 0.0076 | 0.0040 | 0.0191 | +0.0063 |
| Naive Composition | 0.0417 | 0.0081 | 0.1921 | +0.0404 |
| **OpenClaw-Ordered** | **0.1837** | **0.0182** | **0.9203** | **+0.1824** |

**Conflict resolution.** Only OpenClaw-Ordered correctly resolves Scenario 7 (`throttle_vs_serialize_conflict`), returning SERIALIZE (the stricter verdict) while recording both THROTTLE and SERIALIZE interventions in the trace. Scenario 9 (`delegated_remediation_conflict`) returns ESCALATE while preserving ROMA-style delegation lineage, the AARM-style step-up approval, and the async serialization signal, demonstrating that ESCALATE dominates SERIALIZE under the existing verdict order and that the composed trace keeps both interventions visible. Scenario 8 (`audit_reconstruction`) returns DENY while preserving explicit skip markers in the real-adapter benchmark when `audit_trace=True`; the trace exports preserve delegation lineage and module-level skips for audit reconstruction. Naive composition returns ALLOW (short-circuits on first module's ALLOW), hiding the conflict entirely.

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

**Results.** The real-adapter snapshot preserves the same composition semantics: OpenClaw-Ordered still resolves all 11 scenarios correctly, including the policy-laundering case where the sanitized summary remains visible but the original unsafe request survives in trace metadata, and the delegated-remediation conflict where the step-up and serialization interventions must both remain visible in the trace.

**Table 3: Real Adapter Accuracy**

| Strategy | Accuracy | % Correct |
|----------|----------|-----------|
| OpenClaw-Ordered | 11/11 | 100.0% |
| Naive Composition | 1/11 | 9.1% |
| SARC Only | 2/11 | 18.2% |
| AuthZ Only | 5/11 | 45.5% |
| Guardrail Only | 3/11 | 27.3% |
| ROMA Only | 2/11 | 18.2% |
| Async Only | 3/11 | 27.3% |

**Latency (real adapters):** Mean overhead is 0.0052ms with P95 at 0.0092ms—still sub-0.1ms and dominated by adapter plumbing rather than module logic. This confirms that composition overhead is dominated by the resolution function and adapter plumbing, not individual module logic.

### 7.4 Threats to Validity

**Internal validity.** Our scenarios are handcrafted. While they cover diverse failure modes, they may not be exhaustive. Future work should mine real-world agent failure corpora to expand scenario coverage.

**External validity.** Evaluations use in-memory Python modules. Production deployments with networked guardrails, remote authz servers, and model inference will see higher absolute latencies (though relative overhead patterns should hold).

**Generalizability.** Results apply to systems with synchronous module execution and deterministic verdicts. Async governance (eventual consistency) or probabilistic enforcement (sampling-based auditing) are not evaluated.
