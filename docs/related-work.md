# Related Work Matrix

**Access date:** 2026-06-13

This matrix is scoped to the paper’s novelty claim: **composable runtime governance for recursive tool-using/meta-agent systems**. The key gap is not any single control mechanism, but how control, delegation, ordering, conflict resolution, and auditability compose at runtime.

## Summary

| Work | Core contribution | What it does well | What it does not cover for OpenClaw-Govern |
| --- | --- | --- | --- |
| SARC | Compiles constraints into runtime enforcement sites (pre-action, action-time, post-action, escalation) | Strong runtime enforcement framing; auditable constraints | Does not by itself solve composition across heterogeneous governance modules, ordering semantics, or conflict resolution across delegation/async/guardrail layers |
| Overlaying Governance / compositional authorization | Delegation and scope attenuation for agentic access; overlays agent semantics onto existing policies | Formalizes delegation paths and scope attenuation | Focuses on authorization semantics, not the full governance stack: async controls, guardrail arbitration, unified traces, or cross-module conflict resolution |
| Runtime Governance for AI Agents: Policies on Paths | Makes execution path the object of governance; path-dependent policy evaluation | Captures non-deterministic, sequence-sensitive policy risks | Does not provide a compositional governance architecture with multiple heterogeneous modules and deterministic resolution rules |
| Five-Plane Reference Architecture for Runtime Governance of Production AI Agents | Composed authority, mediation points, structured evidence substrate | Strong enterprise/runtime governance architecture and evidence framing | More oriented to a reference architecture for production governance than to recursive agent adapters, module ordering semantics, or benchmarked module composition failures |
| Governance-Aware Agent Telemetry | Closed-loop telemetry-to-enforcement with tamper-evident traces | Strong observability-to-enforcement bridge and cross-agent lineage tracking | Centers telemetry and enforcement loop, but not the abstract composition rules for multiple governance modules with conflicting verdicts |
| Harnessing Embodied Agents: Runtime Governance for Policy-Constrained Execution | Runtime governance layer for embodied execution with admission, monitoring, rollback, human override | Clear separation between cognition and execution oversight | Domain is embodied/robotic execution; does not address meta-agent delegation chains, tool-using agent composition, or unified governance traces across heterogeneous modules |

## Positioning notes

1. **SARC is necessary but not sufficient.**
   - SARC supplies the runtime constraint-enforcement mindset.
   - OpenClaw-Govern extends that into a **composition layer** for multiple governance modules.

2. **Authorization work covers delegation, not the whole stack.**
   - The overlay/compositional authorization line is a good fit for recursive delegation and scope attenuation.
   - Our novelty is broader: we compose authorization with semantic guardrails, async controls, and trace reconciliation.

3. **Path-based governance captures ordering sensitivity but not heterogeneous composition.**
   - Path governance explains why runtime matters.
   - OpenClaw-Govern adds how to resolve disagreements between runtime modules.

4. **Telemetry architectures improve evidence but do not fully define policy composition.**
   - Closed-loop telemetry is complementary.
   - Our paper needs a deterministic governance layer above telemetry so evidence is not fragmented.

5. **Robotics runtime governance is a useful analogy, not the target domain.**
   - It reinforces the runtime-governance pattern.
   - But the paper’s target is recursive tool-using agents and their governance composition failures.

## Sources

- SARC: https://arxiv.org/html/2605.07728v1
- Overlaying Governance: https://arxiv.org/html/2606.03518v1
- Runtime Governance for AI Agents: Policies on Paths: https://arxiv.org/html/2603.16586v1
- Five-Plane Reference Architecture for Runtime Governance of Production AI Agents: https://arxiv.org/html/2606.12320v1
- Governance-Aware Agent Telemetry for Closed-Loop Enforcement in Multi-Agent AI Systems: https://arxiv.org/html/2604.05119v1
- Harnessing Embodied Agents: Runtime Governance for Policy-Constrained Execution: https://arxiv.org/html/2604.07833v3
