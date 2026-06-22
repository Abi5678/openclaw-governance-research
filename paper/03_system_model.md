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

### 4.3 Ver