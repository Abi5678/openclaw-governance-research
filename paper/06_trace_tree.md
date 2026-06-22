## 6. Unified Trace Tree

Governance decisions are only as trustworthy as their auditability. Fragmented traces—where each module logs independently without a unified structure—create three problems:

1. **Reconstruction failure:** Post-hoc auditors cannot determine which modules evaluated an action or in what order.
2. **Tamper vulnerability:** Module-level logs can be altered without detection if not cryptographically linked.
3. **Delegation opacity:** When Agent A delegates to Agent B, traces do not show which constraints propagated and which decisions B inherited from A's authority envelope.

OpenClaw-Govern addresses these with **unified trace trees**—append-only, tamper-evident logs structured by delegation chain and action identity.

### 6.1 Trace Reference Construction

For each action `a` evaluated under delegation chain `D = [a₀, a₁, ..., aₙ]`, the trace reference prefix is:

```
trace_prefix = f"{a₀}>{a₁}>...>{aₙ}:{a.name}"
```

Each module `Mᵢ` appends its decision node:

```
node_ref = f"{trace_prefix}:{Mᵢ.name}:{timestamp}:{decision_hash}"
```

where `decision_hash = SHA256(module || verdict || reason || severity)` provides tamper evidence.

**Example:** For procurement agent chain `research_lead>agent` executing action `buy_gpu`:
```
trace_prefix = "research_lead>agent:buy_gpu"

Module nodes:
  research_lead>agent:buy_gpu:authz:1719086400:0x7f8a…  → ALLOW
  research_lead>agent:buy_gpu:roma:1719086400:0x3c2b…   → ALLOW
  research_lead>agent:buy_gpu:sarc:1719086400:0x9d4e…  → DENY (cost 1200 > cap 500)
  research_lead>agent:buy_gpu:guardrail:1719086400:…    → (skipped, DENY short-circuit)
  research_lead>agent:buy_gpu:asyncfc:1719086400:…      → (skipped)
```

The tree structure makes it immediately clear:
- Which agents participated in the delegation chain
- Which modules executed (and which were short-circuited)
- Which module produced the final verdict
- What rationale each module provided

### 6.2 Tamper Evidence

Each trace node includes a hash of its parent node, forming a hash chain:

```
node_hash[i] = SHA256(node_data[i] || node_hash[i-1])
```

Altering any node invalidates all downstream hashes. The root hash (final node in the chain) can be periodically checkpointed to an external audit log or blockchain for immutable timestamping.

**Implementation note:** Our reference implementation uses in-memory hash chains with periodic export to append-only storage (e.g., AWS QLDB, append-only S3 buckets). Production deployments should integrate with existing audit infrastructure (SIEM, compliance logging systems).

### 6.3 Trace Completeness Metric

We define **trace completeness** as the ability to reconstruct the full decision path for any action:

```
completeness(a) = (modules_executed + modules_short_circuited) / total_modules
```

For ordered composition, `completeness = 1.0` (all modules either execute or are explicitly marked short-circuited). For naive composition with short-circuit, `completeness < 1.0` (downstream modules leave no trace).

**Evaluation finding:** In our governance service benchmark (Section 7.2), OpenClaw-Ordered achieves 100% trace completeness (7/7 cases fully reconstructable), enabling post-hoc audits of every decision path.