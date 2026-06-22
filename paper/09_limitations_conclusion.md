## 9. Limitations

We acknowledge four primary limitations of OpenClaw-Govern:

**1. Scenario coverage.** Our eight composition scenarios are handcrafted to cover identified failure modes. While they demonstrate proof-of-concept, they are not exhaustive. Real production workloads may reveal additional failure modes not captured in our benchmark. Future work should mine real-world agent failure corpora (e.g., incident reports from deployed AI systems) to expand scenario coverage and validate external validity.

**2. Toy vs. production modules.** While Section 7.3 validates composition with real adapters from companion repos (SARC, AuthZ, AsyncFC), these are still controlled research implementations—not battle-tested production governance systems. Our latency measurements (~0.012ms overhead) reflect in-memory Python execution. Production deployments with networked guardrails, remote authorization servers, and model inference will see higher absolute latencies. The relative overhead patterns should hold, but absolute numbers will differ.

**3. Single-agent focus.** All evaluated scenarios test single-agent governance. Multi-agent delegation chains (Agent A → Agent B → Agent C) are modeled via ROMA adapters but not explicitly benchmarked. Future work should add multi-agent scenarios where constraints must propagate across multiple delegation hops, testing whether composition semantics hold at deeper delegation depths.

**4. Synchronous execution.** OpenClaw-Govern assumes synchronous module execution. Async governance models (eventual consistency, probabilistic auditing, sampling-based enforcement) are not addressed. Systems with asynchronous or probabilistic governance may require different composition semantics (e.g., quorum-based voting, temporal consistency windows).

---

## 10. Conclusion

Composition is the missing layer in AI agent governance. Individual control mechanisms—constraints, authorization, guardrails, async controls—are necessary but insufficient. Without defined ordering, conflict arbitration, and unified tracing, composed governance exhibits non-deterministic behavior: bypasses, hidden conflicts, and fragmented audits.

OpenClaw-Govern addresses this gap with four contributions:
1. **Ordered execution** that respects module dependencies and computational cost
2. **Deterministic arbitration** via strict partial order (DENY > ESCALATE > SERIALIZE > THROTTLE > ALLOW)
3. **Delegation-envelope propagation** preserving constraints across authority boundaries
4. **Unified trace trees** enabling post-hoc reconstruction of full decision paths

Our evaluation demonstrates that ordered composition achieves 100% accuracy on eight composition failure modes where naive composition and single-module strategies achieve only 12.5–37.5%. With real governance adapters, accuracy holds with ~0.012ms absolute latency overhead—negligible compared to LLM inference or network RTT.

**Future work.** Three directions:
1. **Multi-agent delegation chains:** Extend evaluation to 3+ hop delegation, testing constraint inheritance depth.
2. **External validation:** Integrate third-party governance modules (not authored by us) to test generalizability.
3. **Production deployment:** Deploy OpenClaw-Govern in real agent systems (e.g., procurement, healthcare, finance) to measure effectiveness under real workloads.

Governance for AI agents is not optional—it is a prerequisite for deployment in high-stakes domains. OpenClaw-Govern provides the composition layer necessary to make governance deterministic, auditable, and composable across heterogeneous mechanisms.

---

## References

[1] SARC: Specification, Assertion, Runtime Control for AI Agents. arXiv:2605.07728, 2026.

[2] Overlaying Governance: Compositional Authorization for Recursive AI Agents. arXiv:2606.03518, 2026.

[3] Runtime Governance for AI Agents: Policies on Paths. arXiv:2603.16586, 2026.

[4] Five-Plane Reference Architecture for Runtime Governance of Production AI Agents. arXiv:2606.12320, 2026.

[5] Governance-Aware Agent Telemetry for Closed-Loop Enforcement. arXiv:2604.05119, 2026.

[6] Harnessing Embodied Agents: Runtime Governance for Policy-Constrained Execution. arXiv:2604.07833, 2026.

[7] ToolEmu: Identifying the Risks of LM Agents with an LM-Emulated Sandbox. arXiv:2309.15817, 2023.

[8] AsyncFC-SARC: Governed Future Orchestrator for Asynchronous Agent Execution. Internal repo, 2026.

[9] τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains. arXiv:2406.12045, 2024.

[10] AgentBench: Evaluating LLMs as Agents. arXiv:2308.03688, 2023.

[11] HELM: Holistic Evaluation of Language Models. https://crfm.stanford.edu/helm/, 2023.

[12] Authenticated Workflows: A Systems Approach to Protecting Agentic AI. arXiv:2602.10465, 2026.

[13] AARM: Autonomous Action Runtime Management. arXiv:2602.09433, 2026.

[14] Multi-Turn Safety Risks in Tool-Using Agents. arXiv:2602.13379, 2026.