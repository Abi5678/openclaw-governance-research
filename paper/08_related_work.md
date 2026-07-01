## 8. Related Work

We position OpenClaw-Govern relative to five categories of prior work: runtime constraint enforcement, authorization and delegation, path-based governance, telemetry architectures, and agent safety benchmarks.

### 8.1 Runtime Constraint Enforcement

**SARC** (Specification, Assertion, Runtime Control) compiles declarative constraints into runtime enforcement sites (pre-action, action-time, post-action, escalation) [1]. SARC's contribution is framing constraints as runtime-enforceable specifications rather than pre-deployment checks. OpenClaw-Govern builds on SARC's enforcement mindset but extends it to **composition**: SARC does not specify how constraint checks compose with heterogeneous modules like authorization, guardrails, or async controllers. Our work provides the missing layer—ordered execution and conflict arbitration—that allows SARC constraints to compose with other governance mechanisms.

### 8.2 Authorization and Delegation

Recent work on **compositional authorization** for AI agents formalizes delegation semantics, scope attenuation, and permission inheritance across trust boundaries [2]. This work answers "Can Agent B act on behalf of Agent A?" but assumes authorization is the sole governance mechanism. OpenClaw-Govern treats authorization as one module among many, defining how authorization verdicts compose with budget constraints, semantic guardrails, and async controls. Our contribution is not delegation semantics themselves, but how delegation-aware composition preserves constraints across authority boundaries. ROMA-style recursive orchestration is a useful contrast case: it gives us delegation structure and traceable decomposition, but it does not arbitrate among heterogeneous runtime controls.

### 8.3 Path-Based Governance

**Policies on Paths** shifts the object of governance from individual actions to action sequences, capturing risks that emerge only in specific execution orders [3]. This work correctly identifies that runtime context matters—two identical actions may have different policy implications depending on preceding actions. OpenClaw-Govern complements this by providing the **mechanism** for path-sensitive evaluation: ordered module execution where async controllers track cumulative risk across sequences. Our contribution is the operationalization of path sensitivity via ordered composition and cumulative context tracking.

### 8.4 Telemetry and Closed-Loop Enforcement

**Governance-Aware Agent Telemetry** bridges observation and enforcement by streaming structured evidence to runtime policy engines [5]. **Five-Plane Architecture** provides a reference model for production governance with composed authority, mediation points, and structured evidence substrates [4]. These works focus on the observation layer—how to collect, transmit, and act on governance telemetry. OpenClaw-Govern operates at the **decision layer**—how to resolve conflicts when multiple policy engines produce competing verdicts. The two are complementary: our unified trace trees (Section 6) adopt the tamper-evident telemetry mindset while adding conflict resolution semantics.

Policy-combining standards such as XACML and audit layers such as OPA decision logs provide a useful precedent for deterministic arbitration and auditable enforcement records [12,13]. They are adjacent to OpenClaw-Govern because they show how policy decisions can be combined and logged, but they stop at access-control boundaries rather than recursive delegation and heterogeneous runtime governance.

### 8.5 Robotics and Embodied Agent Governance

**Runtime Governance for Embodied Agents** applies runtime constraint enforcement to robotic execution, with admission control, monitoring, rollback, and human override [6]. This work reinforces the runtime governance pattern in a different domain (embodied execution vs. tool-using agents). OpenClaw-Govern targets recursive tool-using agents and their unique failure modes (delegation leaks, async correlated risk, fragmented traces). The robotics analogy validates the runtime governance approach but does not address the composition-specific challenges of meta-agent systems.

### 8.6 Agent Safety Benchmarks

**ToolEmu** emulates a sandbox of 36 high-stakes tools to identify risky tool-use failures across 144 test cases [7]. **τ-bench** evaluates tool-agent-user interaction across 40+ turns with policy guidelines and database-state evaluation [9]. **AgentBench** tests LLMs as agents across eight interactive environments [10]. **HELM** provides holistic model evaluation across capabilities, safety, and domain benchmarks [11].

These benchmarks answer "Are agents safe?" by measuring task-level outcomes. OpenClaw-Govern answers a different question: "**Is the governance layer itself correct?**" Our evaluation isolates the composition layer—does ordered execution with deterministic arbitration correctly resolve conflicting verdicts? We cite these benchmarks as motivation (agent safety matters) but distinguish our contribution: we evaluate **governance composition**, not agent capability.

### 8.7 Summary

Table 4 positions OpenClaw-Govern relative to prior work. Checkmarks indicate which dimensions each work addresses. OpenClaw-Govern is the only work addressing all four: ordered execution, conflict arbitration, delegation propagation, and unified traces.

**Table 4: Related Work Positioning**

| Work | Ordered Execution | Conflict Arbitration | Delegation Propagation | Unified Traces |
|------|------------------|---------------------|----------------------|----------------|
| SARC [1] | ✗ | ✗ | ✗ | ✗ |
| Compositional AuthZ [2] | ✗ | ✗ | ✓ | ✗ |
| Policies on Paths [3] | Partial | ✗ | ✗ | ✗ |
| Five-Plane Arch [4] | ✗ | ✗ | ✗ | ✓ |
| Governance Telemetry [5] | ✗ | ✗ | ✗ | ✓ |
| XACML / OPA decision logs [12,13] | ✗ | ✓ | ✗ | ✓ |
| Embodied Governance [6] | ✗ | ✗ | ✗ | ✗ |
| ToolEmu [7], τ-bench [9], AgentBench [10], HELM [11] | ✗ | ✗ | ✗ | ✗ |
| **OpenClaw-Govern** | **✓** | **✓** | **✓** | **✓** |