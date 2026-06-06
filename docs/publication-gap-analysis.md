# Publication Gap Analysis

## What already exists

### SARC

SARC already contributes governance-by-architecture: constraints compiled into structural enforcement sites such as pre-action gates, action-time monitoring, post-action auditing, and escalation routing.

### Authorization propagation

The authorization propagation work focuses on preserving identity and permission invariants across multi-agent delegation chains.

### TrinityGuard / guardrail-style systems

Risk taxonomies and guardrail checks classify or block unsafe behaviors, often at semantic or policy levels.

### AsyncFC-style execution

Future-based and concurrent tool execution needs risk-aware mediation because parallel tool calls can bypass sequential assumptions.

### ROMA-style delegation/memory/runtime adapters

Recursive or hierarchical agent delegation introduces chain-of-custody and runtime mediation concerns.

## What is not enough for publication

- Implementing SARC again.
- Showing one SARC demo.
- Adding a guardrail wrapper around an agent.
- Making a dashboard without evaluation.
- Showing a hackathon agent with governance labels.

## Research gap

The missing layer is **composition**.

Open problems:

1. Ordering failure
   - A policy check runs before identity is established.
   - A tool call is allowed before async risk is evaluated.

2. Conflict failure
   - One module allows while another blocks.
   - No explicit rule decides outcome.

3. Delegation leak
   - A child agent receives broader permissions than the parent intended.

4. Async bypass
   - Individually safe calls become unsafe when run concurrently.

5. Audit fragmentation
   - Each module logs separately, so no one can reconstruct the actual decision path.

6. Escalation ambiguity
   - Human review is required but no module owns the escalation decision.

7. Policy laundering
   - Unsafe intent is transformed through tool outputs or intermediate summaries and bypasses output-only checks.

## Novel contribution

OpenClaw-Govern is research-worthy if it provides:

- a taxonomy of composition-specific governance failures;
- a runtime adapter model for heterogeneous governance modules;
- ordering and conflict semantics;
- unified audit traces;
- a benchmark that demonstrates failures single mechanisms miss.
