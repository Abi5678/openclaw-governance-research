# OpenClaw-Govern Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Agent Action Request                             │
│                      (tool call, delegation, async)                      │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    OpenClaw-Govern Composition Layer                     │
│                                                                          │
│  ┌────────────┐                                                          │
│  │   Context  │←─ Delegated from parent chain                           │
│  │ Repository │   - cost_caps                                           │
│  │            │   - delegation_chain                                    │
│  │            │   - group_risk                                          │
│  │            │   - trace_prefix                                        │
│  └─────┬──────┘                                                          │
│        │                                                                  │
│        ▼                                                                  │
│  ┌────────────────────────────────────────────────────────────┐         │
│  │              Ordered Module Execution (O = [M₁..Mₖ])       │         │
│  │                                                            │         │
│  │    ┌─────────┐  ┌────────┐  ┌───────┐  ┌─────────┐        │         │
│  │    │  AuthZ  │→ │  ROMA  │→ │ SARC  │→ │Guardrail│  → ... │         │
│  │    │ (fast)  │  │(deleg.)│ │(budget)│ │ (slow)  │        │         │
│  │    └────┬────┘  └───┬────┘  └───┬───┘  └────┬────┘        │         │
│  │         │           │           │           │              │         │
│  │         ▼           ▼           ▼           ▼              │         │
│  │   ALLOW/       ALLOW/      ALLOW/       ALLOW/             │         │
│  │   DENY         DENY        DENY         DENY               │         │
│  │                                │           │               │         │
│  │                                └─────┬─────┘               │         │
│  │                                      │                     │         │
│  └──────────────────────────────────────┼─────────────────────┘         │
│                                         │                                 │
│                                         ▼                                 │
│                                ┌────────────────┐                        │
│                                │   Resolution   │                        │
│                                │   Function     │                        │
│                                │ resolve()      │                        │
│                                └────────┬───────┘                        │
│                                         │                                 │
│                                         ▼                                 │
│                              DENY > ESCALATE > SERIALIZE >                │
│                              THROTTLE > ALLOW                             │
│                                         │                                 │
└─────────────────────────────────────────┼─────────────────────────────────┘
                                          │
                                          ▼
                              ┌───────────────────────┐
                              │   Final Verdict       │
                              │   + Unified Trace     │
                              │   + Interventions     │
                              └───────────────────────┘
                                          │
                                          ▼
                              ┌───────────────────────┐
                              │   Tool Execution      │
                              │   (or BLOCKED)        │
                              └───────────────────────┘
```

**Key properties:**
1. **Ordered execution** - Modules run in fixed order (fast→slow, specific→general)
2. **Context propagation** - Shared `GovernanceContext` carries DelegationChain, cost caps, group risk across modules
3. **Deterministic arbitration** - `resolve()` returns max(verdicts) using strict partial order
4. **Unified traces** - Every module decision logged to tamper-evident trace tree

---

## Figure Notes

This diagram shows:
- **Top:** Agent initiates action (tool call, delegation, async execution)
- **Middle:** OpenClaw-Govern intercepts with composition layer
  - Context repository holds delegation chain, inherited constraints, cumulative metrics
  - Modules execute in order: AuthZ (fast, token validity) → ROMA (delegation) → SARC (budget) → Guardrail (semantic) → AsyncFC (correlation)
  - Each module sees same context, writes decisions to trace
  - Context is mutable: AsyncFC can update `group_risk` seen by later modules
- **Resolution:** Arbitration function applies strict partial order
- **Bottom:** Final verdict + trace emitted; action proceeds or blocked

**Visual style for final paper:**
- Replace ASCII with clean vector diagram (draw.io, Lucidchart, or TikZ)
- Use consistent color scheme (e.g., blue for context, green for modules, orange for arbitration)
- Add callout boxes explaining key design decisions
- Include example module verdicts (e.g., "AuthZ: ALLOW, SARC: DENY → Final: DENY")