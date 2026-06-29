# OpenClaw Team — Shared Handoff Protocol

This directory is the persistent handoff surface between the three standing cron teammates:
researcher → builder → reviewer.

Each teammate reads from this directory on its scheduled run, writes a dated artifact,
and either advances the queue or stops cleanly.

## Layout

team/
  STATE.md              — current status, last action per role, blockers
  RESEARCH_<DATE>.md    — researcher's pick + rationale (input to builder)
  BUILDER_<DATE>.md     — builder's plan + change summary (input to reviewer)
  REVIEW_<DATE>.md      — reviewer's verdict + findings
  QUEUE.md              — ordered list of pending work items (research maintains)
  HISTORY.md            — append-only log of transitions

## State machine

   IDLE → RESEARCHER writes RESEARCH_*.md → BUILDER picks top of QUEUE → writes BUILDER_*.md → REVIEWER audits → writes REVIEW_*.md → back to IDLE

## Constraints (enforced by every team member)

- Each role runs exactly one bounded increment per cron tick.
- No teammate may push to main; only reviewer (after APPROVED verdict) commits and pushes.
- No teammate may start a fresh run while STATE.md shows a teammate still IN_PROGRESS.
- If a teammate is blocked, it appends a BLOCKED entry to HISTORY.md and exits.
