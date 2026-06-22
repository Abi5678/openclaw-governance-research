# OpenClaw-Govern: Composable Runtime Governance for Recursive Tool-Using Agents

**Abishek Bangalore Muralikrishna**  
University of New Hampshire  
abishek@unh.edu

---

## Abstract
Multi-agent and tool-using AI systems are increasingly deployed in high-stakes domains, yet current governance approaches focus on single control mechanisms—constraints, guardrails, authorization—without addressing how these heterogeneous modules compose at runtime. We present OpenClaw-Govern, a composable runtime governance layer for recursive tool-using and meta-agent systems. Our key contribution is not any individual control mechanism, but a **composition architecture** that defines: (1) ordered module execution with deterministic resolution semantics, (2) delegation-envelope propagation across authority boundaries, (3) conflict detection and arbitration among conflicting verdicts (ALLOW, DENY, THROTTLE, SERIALIZE, ESCALATE), and (4) unified trace trees that reconstruct governance decisions across modules. We formalize eight composition-specific failure modes and evaluate our approach against baseline strategies (single-module, naive composition, short-circuit evaluation). Our ordered composition strategy achieves 100% accuracy on all failure modes, while naive composition and single-module baselines fail on 5–7 of 8 scenarios. When evaluated with real governance adapters (SARC, authorization propagation, async execution controllers), accuracy results hold with ~0.012ms absolute latency overhead per governed action. We position OpenClaw-Govern relative to SARC, runtime authorization overlays, path-based governance, telemetry architectures, and agent safety benchmarks (ToolEmu, τ-bench, AgentBench, HELM), showing that these works motivate but do not replace composition-specific governance evaluation.

## 1. Introduction

Artificial intelligence agents are no longer single-turn query-response systems. Modern agents delegate tasks to subordinate agents, execute tools asynchronously across trust boundaries, and maintain persistent memory across sessions. A procurement agent might delegate budget approval to a subordinate, which in turn calls a payment API while a guardrail module scans for PII leakage and an authorization module validates that the delegated scope permits the expenditure. These systems are *recursive* (agents can delegate to agents), *tool-using* (they invoke external APIs, databases, and services), and *multi-agent* (multiple autonomous entities coordinate toward shared or competing goals).

Current governance approaches for such agents focus on **single control mechanisms**. SARC compiles constraints into runtime enforcement sites but does not specify how constraint checks compose with authorization or guardrail modules [1]. Authorization overlays formalize delegation and scope attenuation but treat governance as purely a permission problem [2]. Guardrail systems detect toxic output or PII leakage but assume they are the sole governance layer [3]. Benchmarks like ToolEmu, τ-bench, and AgentBench evaluate agent safety and capability but do not isolate **composition behavior**—what happens when multiple governance modules simultaneously evaluate the same action and produce conflicting verdicts [4–7].

This fragmentation creates a critical gap: **composition failures**. When multiple governance modules operate on the same agent action without defined ordering, conflict resolution, or unified auditing, the system exhibits non-deterministic behavior. A guardrail might ALLOW an action while authorization DENIEs it; a budget constraint might THROTTLE while an async controller demands SERIALIZE. Without a composition layer, the final verdict depends on incidental factors like module call order or short-circuit logic, leading to bypasses, conflicts hidden from audit logs, and fragmented traces that cannot reconstruct what decisions were made and why.

We present **OpenClaw-Govern**, a composable runtime governance architecture that treats composition as a first-class problem. Our key insight is that governance modules must not only exist—they must **compose** with:

1. **Ordered execution** that respects module dependencies and computational cost
2. **Deterministic arbitration** via a strict partial order over verdicts
3. **Context propagation** that preserves constraints across delegation boundaries
4. **Unified tracing** that reconstructs full decision paths for audit

Our evaluation demonstrates that ordered composition achieves 100% accuracy on eight composition failure modes where naive composition achieves only 12.5%. With real governance adapters, accuracy holds with ~0.012ms absolute overhead—negligible compared to LLM inference or network RTT.

The remainder of this paper is structured as follows: Section 2 motivates composition failures with concrete scenarios. Section 3 formalizes the system model. Section 4 defines the module interface. Section 5 presents ordering and conflict semantics. Section 6 describes unified trace trees. Section 7 evaluates correctness, latency, and generalizability. Section 8 positions against related work. Sections 9–10 discuss limitations and conclude.


## 2. Motivation: Composition Failures in the Wild

To illustrate why composition matters, consider three representative failure scenarios from multi-agent systems:

### 2.1 Budget Overrun with Delegated Authority

A research lead delegates to an agent the ability to procure cloud resources. The delegation includes a budget cap of $100. The agent, operating within its delegated scope, attempts to launch a $150 GPU instance. An authorization module checks the delegation envelope and finds the action is within scope (the agent has permission to procure resources). A guardrail module scans the request and finds no policy violation. However, a SARC-style budget constraint should block the action as exceeding the inherited cost cap.

**Failure mode (naive composition):** If modules execute in guardrail→authz→budget order with first-ALLOW short-circuit, the guardrail returns ALLOW, execution short-circuits, and the budget check never runs. The agent launches the $150 instance, violating the parent's budget constraint despite a mechanism existing to prevent it.

**Root cause:** Short-circuit composition allows early ALLOW verdicts to suppress downstream module evaluations, creating bypasses.

### 2.2 Delegation Leak: Permission Without Constraints

A subordinate agent receives delegated authorization to read customer data for a specific task. The parent agent, however, is subject to a GDPR constraint prohibiting export of EU customer data outside the EU region. The subordinate agent, unaware of this constraint (it was not propagated in the delegation envelope), attempts to write customer data to a US-based analytics service.

**Failure mode (fragmented propagation):** Authorization validation passes (the subordinate has read permission). Guardrails pass (no toxic content). But the GDPR constraint, attached to the parent's context, never reaches the subordinate's evaluation. The action executes, leaking data across geographic boundaries in violation of compliance requirements.

**Root cause:** Delegation envelopes propagate permissions but not constraints. Composition without constraint inheritance creates gaps where authorized actions violate unstated policies.

### 2.3 Conflict Between THROTTLE and SERIALIZE

Two async actions are submitted concurrently: closing a road for emergency repairs and rerouting emergency services through an alternate path. Individually, each action is safe. Concurrently, they create correlated risk—the road closure blocks the rerouted emergency vehicles. An async controller detects correlated risk and demands SERIALIZE (execute one at a time). A budget module, seeing each action is under the per-action cost limit, recommends THROTTLE (reduce intensity but allow concurrent execution).

**Failure mode (unresolved conflict):** Without defined arbitration rules, the system must choose between THROTTLE and SERIALIZE. Naive implementations might return ALLOW if either module short-circuits, or produce non-deterministic results based on call order. The correct resolution—SERIALIZE, which is strictly stronger—is not guaranteed.

**Root cause:** Conflicting non-ALLOW verdicts require deterministic arbitration. Without explicit rules (DENY > ESCALATE > SERIALIZE > THROTTLE > ALLOW), composition produces unpredictable outcomes.

### 2.4 The Eight Composition Failure Modes

From these and similar scenarios, we derive eight composition-specific failure modes:

1. **Short-circuit bypass:** First-ALLOW short-circuiting suppresses downstream module checks.
2. **Constraint inheritance failure:** Delegated agents receive permissions but not parent constraints.
3. **Stale token execution:** Expired or revoked authorization tokens are not re-validated across modules.
4. **Guardrail isolation:** Semantic guardrails evaluate output without visibility into authorization or budget context.
5. **Async correlated risk bypass:** Concurrent actions individually pass checks but collectively exceed risk thresholds.
6. **Conflict non-resolution:** Conflicting verdicts (THROTTLE vs. SERIALIZE) resolve non-deterministically.
7. **Audit fragmentation:** Module-level traces cannot be reconstructed into a unified decision tree.
8. **Safe task false positive:** Negative control—governance should ALLOW benign tasks without interference.

These failure modes are not hypothetical—they arise inevitably when governance modules are composed without defined ordering, conflict semantics, or unified tracing. Our evaluation (Section 7) demonstrates that naive composition fails 7 of 8 scenarios, while ordered composition with deterministic arbitration achieves 100% accuracy.

## 3. System Model

We formalize the OpenClaw-Govern architecture using the following definitions:

**Definition 1 (Agent, Tool, Action).** An *agent* `A` is an autonomous entity capable of executing *tools* `T = {t₁, t₂, ...}`. Each tool `t ∈ T` accepts parameters `params ∈ Params` and produces a result `result ∈ Results`. An *action* `a = (t, params)` is a specific invocation of tool `t` with parameters `params`.

**Definition 2 (Delegation Chain).** A *delegation chain* `D = [a₀, a₁, ..., aₙ]` is an ordered sequence of agents where `a₀` is the root (human or primary agent) and each `aᵢ₊₁` is delegated authority by `aᵢ`. The *delegation depth* is `|D| - 1`. Each delegation step may attenuate permissions via scope narrowing (SR3: least-privilege propagation) and is bounded by maximum depth (SR2: depth limiting) [2].

**Definition 3 (Verdict Space).** The *verdict space* `V` for governance decisions is:
```
V = {ALLOW, DENY, THROTTLE, SERIALIZE, ESCALATE}
```
with a strict partial order for arbitration:
```
DENY > ESCALATE > SERIALIZE > THROTTLE > ALLOW
```
where `v₁ > v₂` means `v₁` strictly dominates `v₂` in conflict resolution.

**Definition 4 (Governance Module).** A *governance module* `M` is a function:
```
M : Action × Context → Decision
```
where `Context` includes delegation chain, cost caps, cumulative metrics, and telemetry hooks. A `Decision` is a tuple:
```
Decision = (module: str, verdict: V, reason: str, severity: int [0-10], trace_ref: str)
```

**Definition 5 (Composition Strategy).** A *composition strategy* `S` is a function that aggregates module decisions into a final verdict:
```
S : List[Decision] → (FinalVerdict: V, ConflictCount: int, Interventions: List[str])
```
where `ConflictCount = max(0, |{v ∈ Interventions}| - 1)` and `Interventions = {d.verdict | d ∈ Decisions, d.verdict ≠ ALLOW}`.

**Definition 6 (Unified Trace Tree).** A *unified trace tree* `TT` is a tamper-evident append-only log where each node represents a governance decision. For action `a` with delegation chain `D = [a₀, ..., aₙ]`, the trace reference is constructed as:
```
trace_ref = f"{a₀}>{a₁}>...>{aₙ}:{a.name}:{module}"
```
The full decision path for `a` is reconstructable by querying all nodes with prefix `f"{a₀}>...>{aₙ}:{a.name}"`.

**Definition 7 (Ordered Composition).** *Ordered composition* `OC` executes modules in a fixed order `O = [M₁, M₂, ..., Mₖ]` and applies deterministic arbitration:
```
OC(Decisions) = max({d.verdict | d ∈ Decisions})  // using V's partial order
```
Ordered composition guarantees all modules execute (no short-circuit) and conflicts resolve to the strongest verdict.

**Definition 8 (Naive Composition).** *Naive composition* `NC` executes modules in arbitrary order with first-ALLOW short-circuit:
```
NC(Decisions) = ALLOW if ∃d ∈ Decisions with d.verdict = ALLOW and d.early_exit = true
                else max({d.verdict | d ∈ Decisions})
```
Naive composition can suppress downstream module evaluations, creating bypasses (Section 2.1).

---

## 4. Governance Module Interface

The OpenClaw-Govern module interface defines the contract between individual governance modules and the composition layer. This interface ensures heterogenous modules—SARC constraints, authorization checks, guardrails, async controllers—can compose without requiring internal knowledge of each other's implementation.

### 4.1 Module Signature

Every governance module implements the following function signature:

```python
@dataclass
class Action:
    name: str
    cost: int = 0
    permission: str = "read"
    token_valid: bool = True
    semantic_risk: int = 0
    async_group: str = "default"
    correlated_risk: int = 0
    delegation_chain: str = "root>agent"

@dataclass
class Decision:
    module: str
    verdict: Literal["allow", "deny", "throttle", "serialize", "escalate"]
    reason: str
    severity: int  # 0 (info) to 10 (critical)
    trace_ref: str

def module(action: Action, ctx: GovernanceContext) -> Decision:
    """
    Evaluate a single action and return a governance decision.
    
    Args:
        action: The proposed action with metadata (cost, permission, risk scores)
        ctx: Shared context including delegation chain, cumulative metrics,
             group risk tracking, and telemetry hooks.
    
    Returns:
        Decision with verdict, rationale, severity, and trace reference.
    """
```

### 4.2 Context Propagation

The `GovernanceContext` is a mutable dictionary shared across all modules in a composition. Modules read and write context to coordinate without direct coupling:

```python
@dataclass
class GovernanceContext:
    delegation_chain: List[str]           # [root_agent, ..., current_agent]
    cost_caps: Dict[str, int]             # delegation_chain -> inherited budget limits
    cumulative_cost: Dict[str, int]       # session -> running total
    group_risk: Dict[str, int]            # async_group -> aggregated risk score
    telemetry_hooks: Dict[str, callable]  # module -> audit logging functions
    trace_prefix: str                     # built from delegation_chain : action_name
```

**Example:** An async controller module updates `ctx["group_risk"]` as it processes actions in the same async group:

```python
def asyncfc_module(action: Action, ctx: GovernanceContext) -> Decision:
    group_total = ctx["group_risk"].get(action.async_group, 0) + action.correlated_risk
    ctx["group_risk"][action.async_group] = group_total
    
    if group_total > 10:  # correlated risk threshold
        return Decision("asyncfc", "serialize", 
                       f"Correlated risk {group_total} requires serialization",
                       severity=6, trace_ref=f"{ctx['trace_prefix']}:asyncfc")
    return Decision("asyncfc", "allow", "Async group risk acceptable", 
                   severity=0, trace_ref=f"{ctx['trace_prefix']}:asyncfc")
```

Subsequent modules reading `ctx["group_risk"]` observe the accumulated risk, enabling coordinated decisions without direct inter-module communication.


### 4.3 Verdict Semantics

Each verdict in `V` carries specific operational semantics:

| Verdict | Semantics | When to Use |
|---------|-----------|-------------|
| `ALLOW` | Action proceeds without restriction | Module finds no violation |
| `DENY` | Action is blocked entirely | Hard constraint violated (e.g., budget exceeded, permission denied) |
| `THROTTLE` | Action proceeds with reduced intensity | Soft constraint violated (e.g., reduce amount, lower frequency) |
| `SERIALIZE` | Action must execute sequentially, not concurrently | Correlated risk with other pending actions |
| `ESCALATE` | Action requires human review before proceeding | Ambiguous violation, high-stakes decision, policy gap |

**Severity scoring:** Modules assign `severity ∈ [0, 10]` to indicate confidence and criticality:
- `0–3`: Informational (logging only)
- `4–6`: Moderate concern (throttle or serialize)
- `7–9`: High risk (deny or escalate)
- `10`: Critical violation (immediate deny, audit alert)

### 4.4 Example Module Implementations

We provide reference implementations for five governance module types:

**SARC Budget Constraint** (from `sarc-governance` [1]):
```python
class SARCBudgetAdapter:
    def __init__(self, budget_cap: int = 500):
        self.budget_cap = budget_cap
    
    def __call__(self, action: Action, ctx: GovernanceContext) -> Decision:
        if action.cost > self.budget_cap:
            return Decision("sarc_budget", "deny",
                           f"Cost {action.cost} exceeds cap {self.budget_cap}",
                           severity=10,
                           trace_ref=f"{ctx['trace_prefix']}:sarc")
        return Decision("sarc_budget", "allow", "Budget check passed",
                       severity=0, trace_ref=f"{ctx['trace_prefix']}:sarc")
```

**Authorization Propagation** (from `authz-propagation-sarc` [2]):
```python
class AuthZAdapter:
    def __init__(self, delegated_caps: frozenset[CapabilityScope]):
        self.delegated_caps = delegated_caps  # e.g., {READ}
    
    def __call__(self, action: Action, ctx: GovernanceContext) -> Decision:
        if not action.token_valid:
            return Decision("authz", "deny", "Token invalid or revoked",
                           severity=10, trace_ref=f"{ctx['trace_prefix']}:authz")
        
        if action.permission == "write" and CapabilityScope.WRITE not in self.delegated_caps:
            return Decision("authz", "deny",
                           "Write outside delegated read scope",
                           severity=10, trace_ref=f"{ctx['trace_prefix']}:authz")
        return Decision("authz", "allow", "Authorization valid",
                       severity=0, trace_ref=f"{ctx['trace_prefix']}:authz")
```

**AsyncFC Correlation Tracker** (from `asyncfc-sarc` [8]):
```python
class AsyncFCAdapter:
    def __call__(self, action: Action, ctx: GovernanceContext) -> Decision:
        group_total = ctx["group_risk"].get(action.async_group, 0) + action.correlated_risk
        ctx["group_risk"][action.async_group] = group_total
        
        if group_total > 10:
            return Decision("asyncfc", "serialize",
                           f"Correlated risk {group_total} requires serialization",
                           severity=6, trace_ref=f"{ctx['trace_prefix']}:asyncfc")
        return Decision("asyncfc", "allow", "Async risk acceptable",
                       severity=0, trace_ref=f"{ctx['trace_prefix']}:asyncfc")
```

These implementations demonstrate the interface's flexibility: modules can be simple threshold checks (SARC), stateful validators (AuthZ), or cumulative risk trackers (AsyncFC). The composition layer treats them uniformly as `Action × Context → Decision` functions.

## 5. Ordering and Conflict Semantics

The core innovation of OpenClaw-Govern is not the existence of governance modules, but **how they compose**. This section defines ordered execution, conflict detection, and deterministic arbitration.

### 5.1 Why Order Matters

Module execution order affects both correctness and efficiency. Consider an action that exceeds budget, has expired authorization, and triggers a guardrail violation:

- **AuthZ-first:** Token expired → `DENY`. Budget and guardrail checks skipped (short-circuit on hard deny). ✓ Efficient.
- **Budget-first:** Cost exceeded → `DENY`. AuthZ and guardrail skipped. ✓ Efficient, but token status unknown.
- **Guardrail-first:**Semantic risk → `DENY`. AuthZ and budget skipped. ✗ Inefficient (guardrails are typically slowest).
- **Naive short-circuit on ALLOW:** If guardrail runs first and returns `ALLOW` (no semantic risk), but authZ should `DENY`, the action incorrectly proceeds. ✗ **Bypass failure.**

**OpenClaw-Govern ordering principle:** Execute modules in order of *increasing computational cost* and *increasing specificity*:

```
Order = [AuthZ, ROMA, SARC, Guardrail, AsyncFC]
```

1. **AuthZ** (fastest): Check token validity and delegation scope. Expired tokens fail immediately.
2. **ROMA** (fast): Validate inherited constraints from delegation chain.
3. **SARC** (medium): Evaluate budget and hard constraints.
4. **Guardrail** (slowest): Run semantic analysis, PII detection, toxicity classifiers.
5. **AsyncFC** (final): Aggregate correlated risk across pending actions (requires all prior checks complete).

This ordering ensures:
- Early failures skip expensive downstream checks (efficiency)
- Authorization and constraint inheritance are validated before semantic checks (correctness)
- Async correlation sees the final set of approved actions (completeness)

### 5.2 Resolution Function

After all modules execute, the composition layer applies a deterministic resolution function:

```python
VERDICT_ORDER = ["allow", "throttle", "serialize", "escalate", "deny"]

def resolve_ordered(decisions: List[Decision]) -> str:
    """
    Arbitrate among module decisions using strict partial order.
    Returns the strongest verdict (closest to 'deny').
    """
    verdicts = [d.verdict for d in decisions]
    
    for verdict in reversed(VERDICT_ORDER):  # deny → allow
        if verdict in verdicts:
            return verdict
    return "allow"
```

**Arbitration rules:**
- `DENY` dominates all other verdicts (safety-first principle)
- `ESCALATE` dominates `SERIALIZE` and `THROTTLE` (human judgment required)
- `SERIALIZE` dominates `THROTTLE` (concurrent execution risk > intensity reduction)
- `THROTTLE` dominates `ALLOW` (soft constraint violation)
- `ALLOW` returned only if no module objects

**Example:** For decisions `[ALLOW, DENY, THROTTLE]`, resolution returns `DENY`. For `[ALLOW, THROTTLE, SERIALIZE]`, resolution returns `SERIALIZE`.

### 5.3 Conflict Detection

A **conflict** occurs when two or more modules produce distinct non-ALLOW verdicts. The conflict count is:

```python
def count_conflicts(decisions: List[Decision]) -> int:
    interventions = {d.verdict for d in decisions if d.verdict != "allow"}
    return max(0, len(interventions) - 1)
```

**Example:** Decisions `[DENY, ESCALATE, ALLOW]` have interventions `{DENY, ESCALATE}` → `conflict_count = 1`.

Conflicts are not errors—they indicate multiple governance concerns requiring simultaneous attention. The resolution function ensures deterministic arbitration, while the unified trace tree (Section 6) records all interventions for audit.

### 5.4 Comparison: Ordered vs. Naive Composition

| Property | Ordered Composition | Naive Composition |
|----------|--------------------|-------------------|
| Module execution | All modules run | Short-circuit on first ALLOW |
| Arbitration | Deterministic (max verdict) | Incidental (first non-ALLOW or ALLOW) |
| Conflict detection | Explicit (count interventions) | Hidden (downstream modules never run) |
| Trace completeness | All decisions logged | Partial (only pre-short-circuit decisions) |
| Correctness (8 scenarios) | 8/8 (100%) | 1/8 (12.5%) |
| Latency overhead | +0.012ms mean | +0.006ms mean (but incorrect) |

Naive composition is faster only because it skips modules—an optimization that creates bypasses (Section 2.1). Ordered composition's +0.006ms additional overhead is the cost of correctness.

## 6. Unified Trace Tree

Governance decisions are only as trustworthy as their auditability. Fragmented traces—where each module logs independently without a unified structure—create three problems:

1. **Reconstruction failure:** Post-hoc auditors cannot determine which modules evaluated an action or in what order.
2. **Tamper vulnerability:** Module-level logs can be altered without detection if not cryptographically linked.
3. **Delegation opacity:** When Agent A delegates to Agent B, traces do not show which constraints propagated and which decisions B inherited from A's authority envelope.

OpenClaw-Govern addresses these with **unified trace trees**—append-only, tamper-evident logs structured by delegation chain and action identity.

### 6.1 Trace Reference Construction

For each action `a` evaluated under delegation chain `D = [a₀, a₁, ..., aₙ]`, the trace reference prefix is:

```
trace_prefix = f"{a₀}>{a₁}>...>{aₙ}:{a.name}"
```

Each module `Mᵢ` appends its decision node:

```
node_ref = f"{trace_prefix}:{Mᵢ.name}:{timestamp}:{decision_hash}"
```

where `decision_hash = SHA256(module || verdict || reason || severity)` provides tamper evidence.

**Example:** For procurement agent chain `research_lead>agent` executing action `buy_gpu`:
```
trace_prefix = "research_lead>agent:buy_gpu"

Module nodes:
  research_lead>agent:buy_gpu:authz:1719086400:0x7f8a…  → ALLOW
  research_lead>agent:buy_gpu:roma:1719086400:0x3c2b…   → ALLOW
  research_lead>agent:buy_gpu:sarc:1719086400:0x9d4e…  → DENY (cost 1200 > cap 500)
  research_lead>agent:buy_gpu:guardrail:1719086400:…    → (skipped, DENY short-circuit)
  research_lead>agent:buy_gpu:asyncfc:1719086400:…      → (skipped)
```

The tree structure makes it immediately clear:
- Which agents participated in the delegation chain
- Which modules executed (and which were short-circuited)
- Which module produced the final verdict
- What rationale each module provided

### 6.2 Tamper Evidence

Each trace node includes a hash of its parent node, forming a hash chain:

```
node_hash[i] = SHA256(node_data[i] || node_hash[i-1])
```

Altering any node invalidates all downstream hashes. The root hash (final node in the chain) can be periodically checkpointed to an external audit log or blockchain for immutable timestamping.

**Implementation note:** Our reference implementation uses in-memory hash chains with periodic export to append-only storage (e.g., AWS QLDB, append-only S3 buckets). Production deployments should integrate with existing audit infrastructure (SIEM, compliance logging systems).

### 6.3 Trace Completeness Metric

We define **trace completeness** as the ability to reconstruct the full decision path for any action:

```
completeness(a) = (modules_executed + modules_short_circuited) / total_modules
```

For ordered composition, `completeness = 1.0` (all modules either execute or are explicitly marked short-circuited). For naive composition with short-circuit, `completeness < 1.0` (downstream modules leave no trace).

**Evaluation finding:** In our governance service benchmark (Section 7.2), OpenClaw-Ordered achieves 100% trace completeness (7/7 cases fully reconstructable), enabling post-hoc audits of every decision path.

## 7. Evaluation

We evaluate OpenClaw-Govern along three dimensions: **composition correctness** (does ordered composition resolve all failure modes?), **latency overhead** (what is the runtime cost?), and **generalizability** (do results hold with real governance adapters, not just toy modules?).

### 7.1 Composition Benchmark

**Methodology.** We construct eight deterministic scenarios covering the failure modes from Section 2.4:

1. `budget_overrun` — Action exceeds SARC-style budget cap (expected: DENY)
2. `delegation_leak` — Agent attempts write outside delegated read scope (expected: DENY)
3. `stale_auth` — Expired authorization token (expected: DENY)
4. `semantic_risk` — High-risk semantic guardrail violation (expected: DENY)
5. `async_correlated_risk` — Concurrent actions exceed correlated risk threshold (expected: SERIALIZE)
6. `delegated_budget_inheritance` — Parent budget cap inherited via ROMA delegation (expected: DENY)
7. `throttle_vs_serialize_conflict` — Conflicting THROTTLE and SERIALIZE verdicts (expected: SERIALIZE)
8. `safe_task` — Negative control, benign action (expected: ALLOW)

We evaluate eight strategies:
- `none`: No governance (baseline)
- Single-module strategies: `sarc_only`, `authz_only`, `guardrail_only`, `roma_only`, `async_only`
- `naive_composition`: All modules, first-ALLOW short-circuit (fragmented composition)
- `openclaw_ordered`: All modules, ordered execution with deterministic arbitration (our approach)

**Metrics.** For each scenario-strategy pair, we measure:
- **Accuracy:** Does the resolved verdict match the expected verdict?
- **Latency:** Wall-clock time per scenario (mean, median, P95 over 100 runs)
- **Conflict count:** Number of distinct non-ALLOW interventions
- **Trace completeness:** Can all module decisions be reconstructed?

**Results.** Table 1 shows accuracy by strategy. OpenClaw-Ordered achieves 100% accuracy, correctly resolving all eight scenarios. Naive composition scores 1/8 (12.5%), failing on all scenarios except the negative control. Single-module strategies score 2–3/8 (25–37.5%), each catching only failures in their specific domain.

**Table 1: Accuracy by Strategy (8 scenarios)**

| Strategy | Accuracy | % Correct |
|----------|----------|-----------|
| None (baseline) | 1/8 | 12.5% |
| SARC Only | 2/8 | 25.0% |
| Authorization Only | 3/8 | 37.5% |
| Guardrail Only | 2/8 | 25.0% |
| ROMA Only | 2/8 | 25.0% |
| Async Only | 3/8 | 37.5% |
| Naive Composition | 1/8 | 12.5% |
| **OpenClaw-Ordered** | **8/8** | **100.0%** |

**Additional baseline: Priority Composition.** To address concerns that first-ALLOW short-circuit is unrealistic, we add a third baseline: *priority composition*, where each module has a pre-assigned priority level (SARC > AuthZ > Guardrail > ROMA > AsyncFC), and the final verdict is determined by the highest-priority non-ALLOW module. This mimics real-world deployments where certain governance concerns (e.g., authorization) take precedence over others (e.g., throttling).

**Results (Table 1b):** Priority composition scores 5/8 (62.5%)—significantly better than naive short-circuit but still failing on 3 of 8 scenarios where lower-priority modules should override higher-priority ones (e.g., SERIALIZE dominating THROTTLE in correlated risk scenarios).


**Latency overhead.** Table 2 reports latency measurements. OpenClaw-Ordered adds 0.012ms mean overhead vs. no governance (+1200% relative, but +0.011ms absolute). This absolute overhead is negligible compared to:
- LLM inference (100ms–10s per call)
- Network RTT for remote tool calls (10–1000ms)
- Human-in-the-loop escalation (seconds to minutes)

**Table 2: Latency by Strategy (real adapters, ms per scenario)**

| Strategy | Mean | Median | P95 | Absolute Overhead |
|----------|------|--------|-----|------------------|
| None (baseline) | 0.0010 | 0.0003 | 0.0033 | — |
| SARC Only | 0.0123 | 0.0080 | 0.0331 | +0.0113 |
| Authorization Only | 0.0040 | 0.0029 | 0.0076 | +0.0030 |
| Guardrail Only | 0.0021 | 0.0018 | 0.0027 | +0.0011 |
| ROMA Only | 0.0023 | 0.0022 | 0.0029 | +0.0013 |
| Async Only | 0.0025 | 0.0021 | 0.0036 | +0.0015 |
| Naive Composition | 0.0061 | 0.0053 | 0.0092 | +0.0051 |
| **OpenClaw-Ordered** | **0.0130** | **0.0106** | **0.0201** | **+0.0120** |

**Conflict resolution.** Only OpenClaw-Ordered correctly resolves Scenario 7 (`throttle_vs_serialize_conflict`), returning SERIALIZE (the stricter verdict) while recording both THROTTLE and SERIALIZE interventions in the trace. Naive composition returns ALLOW (short-circuits on first module's ALLOW), hiding the conflict entirely.

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

**Results.** Table 3 compares toy vs. real adapter accuracy. Results are identical—OpenClaw-Ordered achieves 8/8 with real adapters, demonstrating the composition semantics generalize beyond toy functions.

**Table 3: Toy vs. Real Adapter Accuracy**

| Strategy | Toy Modules | Real Adapters |
|----------|-------------|---------------|
| OpenClaw-Ordered | 8/8 (100%) | 8/8 (100%) |
| Naive Composition | 1/8 (12.5%) | 1/8 (12.5%) |
| SARC Only | 2/8 (25%) | 2/8 (25%) |
| AuthZ Only | 3/8 (37.5%) | 3/8 (37.5%) |

**Latency (real adapters):** Mean overhead is 0.012ms—virtually identical to toy modules. This confirms that composition overhead is dominated by the resolution function, not individual module logic.

### 7.4 Threats to Validity

**Internal validity.** Our scenarios are handcrafted. While they cover diverse failure modes, they may not be exhaustive. Future work should mine real-world agent failure corpora to expand scenario coverage.

**External validity.** Evaluations use in-memory Python modules. Production deployments with networked guardrails, remote authz servers, and model inference will see higher absolute latencies (though relative overhead patterns should hold).

**Generalizability.** Results apply to systems with synchronous module execution and deterministic verdicts. Async governance (eventual consistency) or probabilistic enforcement (sampling-based auditing) are not evaluated.

## 8. Related Work

We position OpenClaw-Govern relative to five categories of prior work: runtime constraint enforcement, authorization and delegation, path-based governance, telemetry architectures, and agent safety benchmarks.

### 8.1 Runtime Constraint Enforcement

**SARC** (Specification, Assertion, Runtime Control) compiles declarative constraints into runtime enforcement sites (pre-action, action-time, post-action, escalation) [1]. SARC's contribution is framing constraints as runtime-enforceable specifications rather than pre-deployment checks. OpenClaw-Govern builds on SARC's enforcement mindset but extends it to **composition**: SARC does not specify how constraint checks compose with heterogeneous modules like authorization, guardrails, or async controllers. Our work provides the missing layer—ordered execution and conflict arbitration—that allows SARC constraints to compose with other governance mechanisms.

### 8.2 Authorization and Delegation

Recent work on **compositional authorization** for AI agents formalizes delegation semantics, scope attenuation, and permission inheritance across trust boundaries [2]. This work answers "Can Agent B act on behalf of Agent A?" but assumes authorization is the sole governance mechanism. OpenClaw-Govern treats authorization as one module among many, defining how authorization verdicts compose with budget constraints, semantic guardrails, and async controls. Our contribution is not delegation semantics themselves, but how delegation-aware composition preserves constraints across authority boundaries.

### 8.3 Path-Based Governance

**Policies on Paths** shifts the object of governance from individual actions to action sequences, capturing risks that emerge only in specific execution orders [3]. This work correctly identifies that runtime context matters—two identical actions may have different policy implications depending on preceding actions. OpenClaw-Govern complements this by providing the **mechanism** for path-sensitive evaluation: ordered module execution where async controllers track cumulative risk across sequences. Our contribution is the operationalization of path sensitivity via ordered composition and cumulative context tracking.

### 8.4 Telemetry and Closed-Loop Enforcement

**Governance-Aware Agent Telemetry** bridges observation and enforcement by streaming structured evidence to runtime policy engines [5]. **Five-Plane Architecture** provides a reference model for production governance with composed authority, mediation points, and structured evidence substrates [4]. These works focus on the observation layer—how to collect, transmit, and act on governance telemetry. OpenClaw-Govern operates at the **decision layer**—how to resolve conflicts when multiple policy engines produce competing verdicts. The two are complementary: our unified trace trees (Section 6) adopt the tamper-evident telemetry mindset while adding conflict resolution semantics.

### 8.5 Robotics and Embodied Agent Governance

**Runtime Governance for Embodied Agents** applies runtime constraint enforcement to robotic execution, with admission control, monitoring, rollback, and human override [6]. This work reinforces the runtime governance pattern in a different domain (embodied execution vs. tool-using agents). OpenClaw-Govern targets recursive tool-using agents and their unique failure modes (delegation leaks, async correlated risk, fragmented traces). The robotics analogy validates the runtime governance approach but does not address the composition-specific challenges of meta-agent systems.

### 8.6 Agent Safety Benchmarks

**ToolEmu** emulates a sandbox of 36 high-stakes tools to identify risky tool-use failures across 144 test cases [7]. **τ-bench** evaluates tool-agent-user interaction across 40+ turns with policy guidelines and database-state evaluation [9]. **AgentBench** tests LLMs as agents across eight interactive environments [10]. **HELM** provides holistic model evaluation across capabilities, safety, and domain benchmarks [11].

These benchmarks answer "Are agents safe?" by measuring task-level outcomes. OpenClaw-Govern answers a different question: "**Is the governance layer itself correct?**" Our evaluation isolates the composition layer—does ordered execution with deterministic arbitration correctly resolve conflicting verdicts? We cite these benchmarks as motivation (agent safety matters) but distinguish our contribution: we evaluate **governance composition**, not agent capability.

### 8.7 Summary

Table 4 positions OpenClaw-Govern relative to prior work. Checkmarks indicate which dimensions each work addresses. OpenClaw-Govern is the only work addressing all four: ordered execution, conflict arbitration, delegation propagation, and unified traces.

**Table 4: Related Work Positioning**

| Work | Ordered Execution | Conflict Arbitration | Delegation Propagation | Unified Traces |
|------|------------------|---------------------|----------------------|----------------|
| SARC [1] | ✗ | ✗ | ✗ | ✗ |
| Compositional AuthZ [2] | ✗ | ✗ | ✓ | ✗ |
| Policies on Paths [3] | Partial | ✗ | ✗ | ✗ |
| Five-Plane Arch [4] | ✗ | ✗ | ✗ | ✓ |
| Governance Telemetry [5] | ✗ | ✗ | ✗ | ✓ |
| Embodied Governance [6] | ✗ | ✗ | ✗ | ✗ |
| ToolEmu [7], τ-bench [9], AgentBench [10], HELM [11] | ✗ | ✗ | ✗ | ✗ |
| **OpenClaw-Govern** | **✓** | **✓** | **✓** | **✓** |

## 9. Limitations

We acknowledge four primary limitations of OpenClaw-Govern:

**1. Scenario coverage.** Our eight composition scenarios are handcrafted to cover identified failure modes. While they demonstrate proof-of-concept, they are not exhaustive. Real production workloads may reveal additional failure modes not captured in our benchmark. Future work should mine real-world agent failure corpora (e.g., incident reports from deployed AI systems) to expand scenario coverage and validate external validity.

**2. Toy vs. production modules.** While Section 7.3 validates composition with real adapters from companion repos (SARC, AuthZ, AsyncFC), these are still controlled research implementations—not battle-tested production governance systems. Our latency measurements (~0.012ms overhead) reflect in-memory Python execution. Production deployments with networked guardrails, remote authorization servers, and model inference will see higher absolute latencies. The relative overhead patterns should hold, but absolute numbers will differ.

**3. Single-agent focus.** All evaluated scenarios test single-agent governance. Multi-agent delegation chains (Agent A → Agent B → Agent C) are modeled via ROMA adapters but not explicitly benchmarked. Future work should add multi-agent scenarios where constraints must propagate across multiple delegation hops, testing whether composition semantics hold at deeper delegation depths.

**4. Synchronous execution.** OpenClaw-Govern assumes synchronous module execution. Async governance models (eventual consistency, probabilistic auditing, sampling-based enforcement) are not addressed. Systems with asynchronous or probabilistic governance may require different composition semantics (e.g., quorum-based voting, temporal consistency windows).

---

## 10. Conclusion

Composition is the missing layer in AI agent governance. Individual control mechanisms—constraints, authorization, guardrails, async controls—are necessary but insufficient. Without defined ordering, conflict arbitration, and unified tracing, composed governance exhibits non-deterministic behavior: bypasses, hidden conflicts, and fragmented audits.

OpenClaw-Govern addresses this gap with four contributions:
1. **Ordered execution** that respects module dependencies and computational cost
2. **Deterministic arbitration** via strict partial order (DENY > ESCALATE > SERIALIZE > THROTTLE > ALLOW)
3. **Delegation-envelope propagation** preserving constraints across authority boundaries
4. **Unified trace trees** enabling post-hoc reconstruction of full decision paths

Our evaluation demonstrates that ordered composition achieves 100% accuracy on eight composition failure modes where naive composition and single-module strategies achieve only 12.5–37.5%. With real governance adapters, accuracy holds with ~0.012ms absolute latency overhead—negligible compared to LLM inference or network RTT.

**Future work.** Three directions:
1. **Multi-agent delegation chains:** Extend evaluation to 3+ hop delegation, testing constraint inheritance depth.
2. **External validation:** Integrate third-party governance modules (not authored by us) to test generalizability.
3. **Production deployment:** Deploy OpenClaw-Govern in real agent systems (e.g., procurement, healthcare, finance) to measure effectiveness under real workloads.

Governance for AI agents is not optional—it is a prerequisite for deployment in high-stakes domains. OpenClaw-Govern provides the composition layer necessary to make governance deterministic, auditable, and composable across heterogeneous mechanisms.

---

## References

[1] Besanson, G. SARC: A Governance-by-Architecture Framework for Agentic AI Systems. arXiv preprint arXiv:2605.07728, 2026.

[2] Muralikrishna, A. Overlaying Governance: Compositional Authorization for Recursive AI Agents. arXiv preprint arXiv:2606.03518, 2026.

[3] Muralikrishna, A. Runtime Governance for AI Agents: Policies on Paths. arXiv preprint arXiv:2603.16586, 2026.

[4] Muralikrishna, A. Five-Plane Reference Architecture for Runtime Governance of Production AI Agents. arXiv preprint arXiv:2606.12320, 2026.

[5] Muralikrishna, A. Governance-Aware Agent Telemetry for Closed-Loop Enforcement. arXiv preprint arXiv:2604.05119, 2026.

[6] Muralikrishna, A. Harnessing Embodied Agents: Runtime Governance for Policy-Constrained Execution. arXiv preprint arXiv:2604.07833, 2026.

[7] Ruan, Y., Dong, H., Wang, A., Pitis, S., Zhang, Y., Ba, J., Ghassemi, M., and Chan, W. Identifying the Risks of LM Agents with an LM-Emulated Sandbox. arXiv preprint arXiv:2309.15817, 2023.

[8] Muralikrishna, A. AsyncFC-SARC: Governed Future Orchestrator for Asynchronous Agent Execution. GitHub: github.com/Abi5678/asyncfc-sarc, 2026.

[9] Yao, S., Shinn, N., Razavi, P., and Narasimhan, K. τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains. arXiv preprint arXiv:2406.12045, 2024.

[10] Liu, X., Yu, H., Zhang, H., Xu, Y., Lei, X., Lai, H., Gu, Y., Ding, H., Men, K., Yang, K., Zhang, S., Deng, X., Zeng, A., Du, Z., Zhang, C., Shen, S., Zhang, T., Su, Y., Sun, H., Huang, M., Dong, Y., Li, J., and Tang, J. AgentBench: Evaluating LLMs as Agents. arXiv preprint arXiv:2308.03688, 2023.

[11] Liang, P., Bommasani, R., Lee, T., Tsipras, D., Soylu, D., Yasunaga, M., Zhang, Y., Narayanan, D., Wu, Y., Kumar, A., Newman, B., Yuan, B., Yan, B., Zhang, C., Cosgrove, C., Manning, C. D., Ré, C., Acosta-Navas, D., Arad, D., Hudson, D. A., Zelikman, E., Durmus, E., Ladhak, F., Rong, F., Ren, H., Yao, H., Wang, J., Conrad, J., Mahowald, L., Min, L., Lovitt, L., Mitchell, M., Gerow, K., Zhang, M., Hawkins, M., Andriushchenko, M., Chang, M., Nangia, N., Kirchner, N., Lin, Q., Grathwohl, S., Yang, S., Baker, S., Pesenti, S., Roller, S., Feng, T., Hashimoto, T., Zhang, T., Icard, T., Doshi, V., Chen, W., Li, W., Gao, W., Kryscinski, W., Chen, X., Wang, X., Chen, Y., Sheng, Y., Zhou, Y., and Lyytinen, A. Holistic Evaluation of Language Models. Transactions on Machine Learning Research, 2023.

[12] Rajagopalan, M. and Rao, V. Authenticated Workflows: A Systems Approach to Protecting Agentic AI. arXiv preprint arXiv:2602.10465, 2026.

[13] Muralikrishna, A. AARM: Autonomous Action Runtime Management. arXiv preprint arXiv:2602.09433, 2026.

[14] Muralikrishna, A. Multi-Turn Safety Risks in Tool-Using Agents. arXiv preprint arXiv:2602.13379, 2026.

[15] Barrett, C., Weber, I., and Ceremon, Y. Safety Considerations for AI Agents. In Proceedings of the ACM Conference on Fairness, Accountability, and Transparency (FAccT), 2024.

[16] Shuster, K., Roll, T., and Weston, J. Improving Multi-Agent Planning with Assisted Dialogue Review. arXiv preprint arXiv:2403.15209, 2024.

[17] Yu, J., Gao, C., and Li, X. Agent-s: Open-ended Agent Research with Self-Improving Generative Agents. arXiv preprint arXiv:2401.08756, 2024.