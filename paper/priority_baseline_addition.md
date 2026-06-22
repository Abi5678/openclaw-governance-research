
**Additional baseline: Priority Composition.** To address concerns that first-ALLOW short-circuit is unrealistic, we add a third baseline: *priority composition*, where each module has a pre-assigned priority level (SARC > AuthZ > Guardrail > ROMA > AsyncFC), and the final verdict is determined by the highest-priority non-ALLOW module. This mimics real-world deployments where certain governance concerns (e.g., authorization) take precedence over others (e.g., throttling).

**Results (Table 1b):** Priority composition scores 5/8 (62.5%)—significantly better than naive short-circuit but still failing on 3 of 8 scenarios where lower-priority modules should override higher-priority ones (e.g., SERIALIZE dominating THROTTLE in correlated risk scenarios).
