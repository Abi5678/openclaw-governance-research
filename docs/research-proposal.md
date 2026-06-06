# Research Proposal: OpenClaw-Govern

## One-line thesis

Agent governance should be treated as a compositional runtime systems problem, not as isolated guardrails, isolated SARC constraints, or isolated authorization checks.

## Research question

How can heterogeneous governance mechanisms be composed inside a tool-using agent runtime while preserving safety constraints, authorization invariants, concurrency controls, useful task completion, and auditability?

## Why this is research-worthy

SARC already provides governance-by-architecture. The new contribution is not another SARC implementation. The gap is composition:

- SARC may enforce runtime constraints but not fully model authorization propagation.
- Guardrail systems may catch semantic risk but not tool-level state transitions.
- Authorization propagation may prevent delegation leaks but not async budget overrun.
- Async execution controls may mediate futures but not policy conflict ordering.
- ROMA-style delegation adapters may produce chain-of-custody but not unified cross-module traces.

Real agent deployments need these mechanisms together. Naive composition can introduce new failure modes.

## Hypothesis

A governance composition layer with explicit lifecycle hooks, ordering semantics, conflict resolution, and unified traces will reduce composition-specific bypasses compared to single-mechanism or naive multi-mechanism governance, while maintaining useful task completion.

## Proposed system

OpenClaw-Govern defines:

1. `GovernanceModule`
   - module-level adapter interface
   - supports lifecycle hooks such as `pre_plan`, `pre_action`, `pre_tool`, `post_tool`, `post_action`, `escalate`

2. `GovernanceDecision`
   - normalized decision object: allow, deny, throttle, redact, serialize, escalate
   - includes reason, severity, affected resource, trace metadata

3. `GovernanceContext`
   - shared runtime state: principal, task, tool, permissions, risk, budget, memory scope, concurrency group

4. `OrderingPolicy`
   - identity/authz first
   - hard safety before soft budget
   - async dispatch after per-future risk checks
   - post-action audit after tool results
   - escalation on unresolved conflict

5. `ConflictResolver`
   - deny dominates allow
   - least privilege dominates convenience
   - serialize dominates parallel execution when risk is correlated
   - escalation dominates silent execution for severe conflicts
   - all conflicts become trace events

6. `UnifiedTrace`
   - one trace tree spanning all modules and all agent actions

## Candidate venues

Near-term:

- arXiv preprint
- NeurIPS/ICLR/ICML workshops on agents, safety, trustworthy AI, AI systems
- AAMAS workshops
- FAccT workshops
- ICSE/ASE workshops on software engineering for AI agents

Longer-term:

- ICSE SEIP / ASE / FSE industry or research track if evaluation becomes strong enough
- TMLR if framed as benchmark + systems analysis

## Expected paper type

Best initial type: systems + benchmark paper.

Not just a position paper. The evaluation should demonstrate composition failures and measure whether OpenClaw-Govern fixes them.
