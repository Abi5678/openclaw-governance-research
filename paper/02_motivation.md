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