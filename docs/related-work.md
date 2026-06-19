# Related Work Matrix

**Access date:** 2026-06-18

This matrix is scoped to the paper’s novelty claim: **composable runtime governance for recursive tool-using/meta-agent systems**. The key gap is not any single control mechanism or benchmark, but how control, delegation, ordering, conflict resolution, and auditability compose at runtime.

## Summary

| Work | Core contribution | What it does well | What it does not cover for OpenClaw-Govern |
| --- | --- | --- | --- |
| SARC | Compiles constraints into runtime enforcement sites (pre-action, action-time, post-action, escalation) | Strong runtime enforcement framing; auditable constraints | Does not by itself solve composition across heterogeneous governance modules, ordering semantics, or conflict resolution across delegation/async/guardrail layers |
| Overlaying Governance / compositional authorization | Delegation and scope attenuation for agentic access; overlays agent semantics onto existing policies | Formalizes delegation paths and scope attenuation | Focuses on authorization semantics, not the full governance stack: async controls, guardrail arbitration, unified traces, or cross-module conflict resolution |
| Runtime Governance for AI Agents: Policies on Paths | Makes execution path the object of governance; path-dependent policy evaluation | Captures non-deterministic, sequence-sensitive policy risks | Does not provide a compositional governance architecture with multiple heterogeneous modules and deterministic resolution rules |
| Five-Plane Reference Architecture for Runtime Governance of Production AI Agents | Composed authority, mediation points, structured evidence substrate | Strong enterprise/runtime governance architecture and evidence framing | More oriented to a reference architecture for production governance than to recursive agent adapters, module ordering semantics, or benchmarked module composition failures |
| Governance-Aware Agent Telemetry | Closed-loop telemetry-to-enforcement with tamper-evident traces | Strong observability-to-enforcement bridge and cross-agent lineage tracking | Centers telemetry and enforcement loop, but not the abstract composition rules for multiple governance modules with conflicting verdicts |
| Harnessing Embodied Agents: Runtime Governance for Policy-Constrained Execution | Runtime governance layer for embodied execution with admission, monitoring, rollback, human override | Clear separation between cognition and execution oversight | Domain is embodied/robotic execution; does not address meta-agent delegation chains, tool-using agent composition, or unified governance traces across heterogeneous modules |
| Authenticated Workflows / MAPL | Cryptographic trust layer for agentic workflows across prompts, tools, data, and context | Strong boundary-oriented security model; explicit policy composition and deterministic reject/allow semantics | Emphasizes cryptographic trust and boundary protection more than runtime arbitration among heterogeneous governance modules, ordering semantics, or trace reconciliation |
| AARM | Runtime interception of AI-driven actions with contextual evaluation and tamper-evident receipts | Clear action-layer security boundary; supports allow/deny/modify/defer/step-up decisions | Does not define a composition layer for multiple governance modules, conflict resolution across modules, or benchmarked module ordering |
| MT-AgentRisk | Multi-turn tool-using-agent safety benchmark with decomposed harmful tasks | Captures multi-turn and tool-mediated safety risks that single-turn benchmarks miss | Evaluates harmful task execution, not governance-module composition, delegation propagation, or unified governance traces |
| ToolEmu | LM-emulated sandbox for identifying risky tool-use agent failures across 36 high-stakes tools and 144 test cases | Scales safety evaluation without implementing every tool/environment; explicitly studies private-data leakage, financial loss, and severe tool-use failures | Evaluates agent/tool safety outcomes, but not governance-module composition, authorization propagation, deterministic ordering semantics, or trace reconciliation across multiple runtime controls |
| τ-bench | Dynamic tool-agent-user benchmark with domain API tools, policy guidelines, database-state evaluation, and pass^k reliability | Strong fit for real-world tool use and policy-following reliability under repeated trials | Benchmarks task/policy success for agents, not the composition behavior of independent governance modules or conflicts such as deny vs rewrite vs serialize |
| AgentBench | Multi-environment benchmark for evaluating LLMs as agents in interactive settings | Broad coverage of reasoning, decision-making, long-horizon interaction, and instruction following across eight environments | Focuses on agent capability and failure causes, not runtime governance composition or auditable enforcement semantics |
| HELM | Holistic evaluation framework/leaderboards spanning capabilities, safety, AIR-Bench, domain benchmarks, and other model-evaluation axes | Establishes transparent, multi-metric evaluation practice and living benchmark infrastructure | Model-centric and benchmark-infrastructure focused; does not target recursive tool-agent governance layers, delegation, or cross-module conflict resolution |

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

6. **Agent benchmarks motivate composition-specific evaluation but do not replace it.**
   - ToolEmu, τ-bench, AgentBench, and HELM show how to evaluate tool-use risk, real-world policy following, interactive agent competence, and broad model safety/capability axes.
   - OpenClaw-Govern should cite them as benchmark lineage while making clear that our evaluation unit is the **governance composition layer**: ordered runtime modules, delegated authority envelopes, async controls, intervention conflicts, and unified trace completeness.
   - This supports a benchmark design in which the expected output is not only task success/failure but also whether the composed governance stack produced the right final verdict, preserved the right evidence, and surfaced conflicts deterministically.

## Sources

- SARC: https://arxiv.org/html/2605.07728v1
- Overlaying Governance: https://arxiv.org/html/2606.03518v1
- Runtime Governance for AI Agents: Policies on Paths: https://arxiv.org/html/2603.16586v1
- Five-Plane Reference Architecture for Runtime Governance of Production AI Agents: https://arxiv.org/html/2606.12320v1
- Governance-Aware Agent Telemetry for Closed-Loop Enforcement in Multi-Agent AI Systems: https://arxiv.org/html/2604.05119
- Harnessing Embodied Agents: Runtime Governance for Policy-Constrained Execution: https://arxiv.org/html/2604.07833v3
- Authenticated Workflows: A Systems Approach to Protecting Agentic AI: https://arxiv.org/html/2602.10465v1
- Autonomous Action Runtime Management (AARM): A System Specification for Securing AI-Driven Actions at Runtime: https://arxiv.org/html/2602.09433v1
- Unsafer in Many Turns: Benchmarking and Defending Multi-Turn Safety Risks in Tool-Using Agents: https://arxiv.org/html/2602.13379
- ToolEmu / Identifying the Risks of LM Agents with an LM-Emulated Sandbox: https://arxiv.org/abs/2309.15817
- τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains: https://arxiv.org/abs/2406.12045
- AgentBench: Evaluating LLMs as Agents: https://arxiv.org/abs/2308.03688
- HELM: https://crfm.stanford.edu/helm/
