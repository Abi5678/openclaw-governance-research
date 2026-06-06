# OpenClaw-Governance Research

Research artifact for a publication on **composable runtime governance for agentic AI systems**.

Working paper title:

> OpenClaw-Govern: Composable Runtime Governance for Tool-Using Agentic AI Systems

Core claim:

> SARC, guardrails, authorization propagation, async execution controls, and memory/runtime adapters are useful individually, but real deployments need a principled composition layer. Naive composition creates ordering bugs, conflicting decisions, audit fragmentation, and concurrency bypasses.

This repository turns Abishek's OpenClaw/SARC experiments into a publishable systems + benchmark project.

## Initial source projects inspected

- `Abi5678/sarc-governance` — SARC runtime constraint enforcement
- `Abi5678/trinityguard-sarc-bridge` — TrinityGuard/OWASP risk taxonomy to SARC constraints
- `Abi5678/authz-propagation-sarc` — authorization propagation for non-human principals
- `Abi5678/asyncfc-sarc` — governed async tool execution
- `Abi5678/roma-sarc-adapter` — ROMA/SARC chain-of-custody adapter
- `Abi5678/sarc-budget-governance` — budget/cost governance
- `Abi5678/torch-agent` — real-world civic operations agent case study

## Contribution direction

1. Taxonomy of governance composition failure modes.
2. Governance module adapter interface.
3. Ordering semantics for runtime checks.
4. Conflict resolution rules.
5. Unified governance trace tree.
6. Benchmark of composition-specific agent governance failures.

## Quick experiment

```bash
python3 experiments/composition_benchmark.py
```

This runs a deterministic toy benchmark comparing:

- no governance
- single mechanisms
- naive composition
- ordered composition with conflict resolution

The benchmark is intentionally simple first; it defines the evaluation shape before we plug in real OpenClaw/SARC components.
