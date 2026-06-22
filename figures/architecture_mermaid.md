# OpenClaw-Govern Architecture

```mermaid
graph TD
    A[Agent Action Request] --> B[OpenClaw-Govern Composition Layer]
    
    subgraph Context [Context Repository]
        C1[Delegation Chain]
        C2[Cost Caps]
        C3[Group Risk]
        C4[Trace Prefix]
    end
    
    B --> Context
    
    subgraph Modules [Ordered Module Execution]
        M1[AuthZ<br/><i>Token valid?</i>]
        M2[ROMA<br/><i>Constraints inherited?</i>]
        M3[SARC<br/><i>Budget cap?</i>]
        M4[Guardrail<br/><i>Semantic risk?</i>]
        M5[AsyncFC<br/><i>Correlated risk?</i>]
    end
    
    Context --> M1
    M1 --> M2
    M2 --> M3
    M3 --> M4
    M4 --> M5
    
    subgraph Resolution [Arbitration]
        R[resolve_ordered<br/>DENY > ESCALATE > SERIALIZE > THROTTLE > ALLOW]
    end
    
    M5 --> R
    
    subgraph Output [Final Output]
        O1[Final Verdict]
        O2[Unified Trace]
        O3[Interventions]
    end
    
    R --> Output
    Output --> E{Action Executed?}
    E -->|ALLOW| F[Tool Executes]
    E -->|DENY/OTHER| G[Blocked/Modified]
    
    style R fill:#f9f,stroke:#333,stroke-width:2px
    style Output fill:#bbf,stroke:#333,stroke-width:2px
```

**Figure 1: OpenClaw-Govern Architecture.** Agent actions are intercepted by the composition layer, which executes governance modules in fixed order (AuthZ → ROMA → SARC → Guardrail → AsyncFC). Each module reads/writes to shared `GovernanceContext` and produces a verdict. The resolution function applies deterministic arbitration (DENY > ESCALATE > SERIALIZE > THROTTLE > ALLOW). Final verdict and unified trace are returned to the agent.

---

## Notes for Final Figure

For the actual paper submission, replace this Mermaid diagram with a vector graphic created in:
- **draw.io** (free, exports to SVG/PDF)
- **Lucidchart** (free tier available)
- **TikZ** (LaTeX-native, steep learning curve)
- **Excalidraw** (hand-drawn style, exports to SVG)

**Design recommendations:**
- Use consistent color scheme (e.g., blue for context, green for modules, orange for arbitration)
- Add callout boxes explaining key design decisions
- Include example module verdicts flowing through the pipeline
- Show trace tree construction on the right side