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