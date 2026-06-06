# Integration Inventory

This file records what each existing Abi5678 repo contributes to the OpenClaw-Govern research artifact.

## `sarc-governance`

Useful primitives:

- `ConstraintSpec`
- `ConstraintRegistry`
- `ConstraintClass`: hard / soft
- `VerificationPoint`: pre-action, action-time, post-action, periodic
- `ResponseProtocol`: block, throttle, escalate, log-and-continue, rollback
- `GovernedAgentLoop`
- `TraceTree`

Research role:

SARC is the architectural enforcement substrate. It should be treated as an existing governance module, not as the paper's novelty by itself.

Composition gap exposed:

SARC provides enforcement sites, but composition still needs cross-module ordering, conflict handling, and unified traces when non-SARC modules participate.

## `authz-propagation-sarc`

Useful primitives:

- `AuthorizationToken`
- `AuthorizationBus`
- structural requirements SR1-SR7
- `AuthzGovernedAgentLoop`
- `AuthzConstraintSpec`

Research role:

Covers identity and permission invariants across non-human principal delegation chains.

Composition gap exposed:

Authorization must generally run before SARC/tool governance; otherwise a structurally valid action may still be unauthorized.

## `trinityguard-sarc-bridge`

Useful primitives:

- `SafetyBridgeLoop`
- `Decision`: allow, block, throttle, escalate
- `SafetyAlert`
- TrinityGuard risk registry / OWASP-style risk mapping
- unified report generation

Research role:

Semantic and risk-taxonomy governance module.

Composition gap exposed:

Semantic risk decisions need to be reconciled with authz and runtime constraint decisions. A semantic guardrail block should not be overwritten by a later allow.

## `asyncfc-sarc`

Useful primitives:

- `GovernedFuture`
- governed async executor/orchestrator
- `RiskProfile`
- `GovernanceMode`: pre-emptive, concurrent, post-hoc
- SARC-to-AsyncFC bridge mapping

Research role:

Represents concurrent tool execution governance.

Composition gap exposed:

Sequential governance assumptions break under concurrent futures. Composition must support group-level risk and serialization decisions.

## `roma-sarc-adapter`

Useful primitives:

- `RomaGovernedAdapter`
- `RomaGovernanceConfig`
- `RomaGovernanceStats`
- `RomaActionExecutor`
- trace bridge / chain-of-custody

Research role:

Represents hierarchical delegation and chain-of-custody governance.

Composition gap exposed:

Recursive delegation needs trace propagation and parent-to-child constraint inheritance.

## `sarc-budget-governance`

Useful primitives:

- cost/token budget examples
- benchmark scripts for conservation/token reduction

Research role:

Budget governance scenario and possibly a low-friction reproducible benchmark.

## `torch-agent`

Useful primitives:

- real-world civic operations case study
- FastAPI backend
- SARC runtime file(s)
- operations governance, cuOpt routing, MCP tools, operator confirmation

Research role:

Applied case study demonstrating why composition matters in a real operations workflow.

## First integration target

The first real benchmark should avoid pulling every repo at once. Recommended order:

1. Implement normalized `GovernanceDecision` and adapters.
2. Integrate `sarc-governance` as the first real module.
3. Add `authz-propagation-sarc` for permission/delegation scenarios.
4. Add `asyncfc-sarc` for correlated concurrent-risk scenarios.
5. Add `trinityguard-sarc-bridge` for semantic risk taxonomy scenarios.
6. Add ROMA trace/delegation only after the base benchmark is stable.
