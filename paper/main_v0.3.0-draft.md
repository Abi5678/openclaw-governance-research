# OpenClaw-Govern: Composable Runtime Governance for Recursive Tool-Using Agents

**Abishek Bangalore Muralikrishna**  
University of New Hampshire  
abishek@unh.edu

---

## Abstract

Multi-agent and tool-using AI systems are increasingly deployed in high-stakes domains, yet current governance approaches focus on single control mechanisms—constraints, guardrails, authorization—without addressing how these heterogeneous modules compose at runtime. We present OpenClaw-Govern, a composable runtime governance layer for recursive tool-using and meta-agent systems. Our key contribution is not any individual control mechanism, but a **composition architecture** that defines: (1) ordered module execution with deterministic resolution semantics, (2) delegation-envelope propagation across authority boundaries, (3) conflict detection and arbitration among conflicting verdicts (ALLOW, DENY, THROTTLE, SERIALIZE, ESCALATE), and (4) unified trace trees that reconstruct governance decisions across modules. We formalize eight composition-specific failure modes and evaluate our approach against baseline strategies (single-module, naive composition, short-circuit evaluation). Our ordered composition strategy achieves 100% accuracy on all failure modes, while naive composition and single-module baselines fail on 5–7 of 8 scenarios. When evaluated with real governance adapters (SARC, authorization propagation, async execution controllers), accuracy results hold with ~0.012ms absolute latency overhead per governed action. We position OpenClaw-Govern relative to SARC, runtime authorization overlays, path-based governance, telemetry architectures, and agent safety benchmarks (ToolEmu, τ-bench, AgentBench, HELM), showing that these works motivate but do not replace composition-specific governance evaluation.

---

## 1. Introduction

Artificial intelligence agents are no longer single-turn query-response systems. Modern agents delegate tasks to subordinate agents, execute tools asynchronously across trust boundaries, and maintain persistent memory across sessions. A procurement agent might delegate budget approval to a subordinate, which in turn calls a payment API while a guardrail module scans for PII leakage and an authorization module validates that the delegated scope permits the expenditure. These systems are *recursive* (agents can delegate to agents), *tool-using* (they invoke external APIs, databases, and services), and *multi-agent* (multiple autonomous entities coordinate toward shared or competing goals).

Current governance approaches for such agents focus on **single control mechanisms**. SARC compiles constraints into runtime enforcement sites but does not specify how constraint checks compose with authorization or guardrail modules [1]. Authorization overlays formalize delegation and scope attenuation but treat governance as purely a permission problem [2]. Guardrail systems detect toxic output or PII leakage but assume they are the sole governance layer [3]. Benchmarks like ToolEmu, τ-bench, and AgentBench evaluate agent safety and capability but do not isolate **composition behavior**—what happens when multiple governance modules simultaneously evaluate the same action and produce conflicting verdicts [4–7].

This fragmentation creates a critical gap: **composition failures**. When multiple governance modules operate on the same agent action without defined ordering, conflict resolution, or unified auditing, the system exhibits non-deterministic behavior. A guardrail might ALLOW an action while authorization DENIEs it; a budget constraint might THROTTLE while an async controller demands SERIALIZE. Without a composition layer, the final verdict depends on incidental factors like module call order or short-circuit logic, leading to bypasses, conflicts hidden from audit logs, and fragmented traces that cannot reconstruct what decisions were made and why.

We present **OpenClaw-Govern**, a composable runtime governance architecture that treats composition as a first-class problem. Our key insight is that governance modules must not only exist—they must **compose** with:

1. **Ordered execution** that respects dependency