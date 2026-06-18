# Evaluation Positioning: From Agent Benchmarks to Governance Composition

**Access date for cited web sources:** 2026-06-18

OpenClaw-Govern should position its evaluation as complementary to, not a replacement for, current agent and model benchmarks. Existing benchmarks establish that tool-using agents fail in realistic, high-stakes, multi-step settings. The distinct evaluation claim here is narrower and more systems-oriented: when several runtime governance mechanisms are composed around a recursive tool-using agent, the evaluation unit is the governance stack itself. The key question is not only whether the agent completed the task, but whether the composed controls produced the correct final intervention, preserved the right delegation context, surfaced conflicts deterministically, and emitted a unified trace.

ToolEmu demonstrates the need for scalable tool-use safety evaluation by using an LM-emulated sandbox to test agents against high-stakes tools and scenarios. Its reported benchmark scale--36 tools and 144 test cases--is useful precedent for stressing tool-agent risk without implementing every real environment. However, ToolEmu's primary object is unsafe agent/tool behavior, not the semantics of composing multiple enforcement modules such as SARC budget gates, authorization propagation, guardrails, and async controls. OpenClaw-Govern can therefore cite ToolEmu as evidence that tool-use risks require benchmarked evaluation while claiming a different evaluation target: composition failures among runtime governance mechanisms. Source: https://arxiv.org/abs/2309.15817.

τ-bench is especially relevant because it evaluates language agents in dynamic user conversations with domain API tools and policy guidelines, then compares final database state to an annotated goal state. Its `pass^k` reliability framing is a useful reminder that one successful run is not enough for deployment-oriented evaluation. OpenClaw-Govern should adopt the spirit of repeated, policy-sensitive evaluation but extend the observable outputs: in addition to task/database correctness, each case should score the governance verdict, the ordered intervention path, conflict handling, and trace completeness. Source: https://arxiv.org/abs/2406.12045.

AgentBench provides broad interactive-agent coverage across multiple environments and identifies failures such as weak long-term reasoning, decision-making, and instruction following. This supports the paper's premise that agentic systems need evaluation beyond static text generation. But AgentBench remains primarily a capability benchmark for LLM-as-agent behavior. It does not ask whether independent governance modules were invoked in a safe order, whether inherited delegation constraints dominated later local allows, or whether async correlated risks were reconciled with budget throttling. Source: https://arxiv.org/abs/2308.03688.

HELM contributes the evaluation norm of transparent, multi-metric benchmark reporting across capability, safety, domain, and modality leaderboards. OpenClaw-Govern should follow this norm by reporting not just aggregate accuracy but also per-scenario failure mode, latency overhead, false block rate, bypass rate, conflict count, and trace completeness. The difference is again the level of analysis: HELM is model- and benchmark-infrastructure centered, while OpenClaw-Govern is a runtime systems evaluation of composed enforcement semantics. Source: https://crfm.stanford.edu/helm/.

The resulting evaluation thesis is:

> Existing agent benchmarks evaluate whether agents can complete tasks, follow policies, or avoid unsafe tool behavior. OpenClaw-Govern evaluates whether a heterogeneous runtime governance layer composes correctly when authorization, SARC-style constraints, semantic guardrails, delegation adapters, async controls, and traces interact.

This distinction maps directly to the current benchmark plan. The benchmark should retain standard outcome metrics such as hard violation rate, bypass rate, false block rate, task completion, and latency overhead. It should add composition-specific metrics that are rare in existing agent benchmarks:

1. **Final-verdict correctness:** whether the resolved intervention (`allow`, `deny`, `rewrite`, `throttle`, `serialize`, `escalate`) matches the expected governance outcome.
2. **Ordering sensitivity:** whether the correct result depends on running modules in a declared order, such as authz and delegation adapters before final allow resolution.
3. **Conflict count and conflict resolution:** whether multiple non-allow interventions are detected and deterministically resolved rather than hidden by first-allow or last-writer-wins behavior.
4. **Delegation-envelope preservation:** whether parent constraints such as reduced budget, scope, or chain-of-custody survive child-agent execution and adapter boundaries.
5. **Async composition safety:** whether individually safe actions are re-evaluated as a correlated group before concurrent execution.
6. **Unified trace completeness:** whether the evidence record contains every module decision, action reference, delegation chain, conflict, remediation, and final verdict needed for audit reconstruction.

In paper prose, this allows OpenClaw-Govern to avoid claiming novelty as "another agent benchmark" or "another SARC implementation." The novelty is the composition layer and the benchmark is valuable because it isolates failures that single controls and task-success benchmarks can miss.
