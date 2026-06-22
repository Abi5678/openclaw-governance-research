## 1. Introduction

Artificial intelligence agents are no longer single-turn query-response systems. Modern agents delegate tasks to subordinate agents, execute tools asynchronously across trust boundaries, and maintain persistent memory across sessions. A procurement agent might delegate budget approval to a subordinate, which in turn calls a payment API while a guardrail module scans for PII leakage and an authorization module validates that the delegated scope permits the expenditure. These systems are *recursive* (agents can delegate to agents), *tool-using* (they invoke external APIs, databases, and services), and *multi-agent* (multiple autonomous entities coordinate toward shared or competing goals).

Current governance approaches for such agents focus on **single control mechanisms**. SARC compiles constraints into runtime enforcement sites but does not specify how constraint checks compose with authorization or guardrail modules [1]. Authorization overlays formalize delegation and scope attenuation but treat governance as purely a permission problem [2]. Guardrail systems detect toxic output or PII leakage but assume they are the sole governance layer [3]. Benchmarks like ToolEmu, τ-bench, and AgentBench evaluate agent safety and capability but do not isolate **composition behavior**—what happens when multiple governance modules simultaneously evaluate the same action and produce conflicting verdicts [4–7].

This fragmentation creates a critical gap: **composition failures**. When multiple governance modules operate on the same agent action without defined ordering, conflict resolution, or unified auditing, the system exhibits non-deterministic behavior. A guardrail might ALLOW an action while authorization DENIEs it; a budget constraint might THROTTLE while an async controller demands SERIALIZE. Without a composition layer, the final verdict depends on incidental factors like module call order or short-circuit logic, leading to bypasses, conflicts hidden from audit logs, and fragmented traces that cannot reconstruct what decisions were made and why.

We present **OpenClaw-Govern**, a composable runtime governance architecture that treats composition as a first-class problem. Our key insight is that governance modules must not only exist—they must **compose** with:

1. **Ordered execution** that respects module dependencies and computational cost
2. **Deterministic arbitration** via a strict partial order over verdicts
3. **Context propagation** that preserves constraints across delegation boundaries
4. **Unified tracing** that reconstructs full decision paths for audit

Our evaluation demonstrates that ordered composition achieves 100% accuracy on eight composition failure modes where naive composition achieves only 12.5%. With real governance adapters, accuracy holds with ~0.012ms absolute overhead—negligible compared to LLM inference or network RTT.

The remainder of this paper is structured as follows: Section 2 motivates composition failures with concrete scenarios. Section 3 formalizes the system model. Section 4 defines the module interface. Section 5 presents ordering and conflict semantics. Section 6 describes unified trace trees. Section 7 evaluates correctness, latency, and generalizability. Section 8 positions against related work. Sections 9–10 discuss limitations and conclude.
