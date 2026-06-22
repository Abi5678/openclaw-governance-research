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