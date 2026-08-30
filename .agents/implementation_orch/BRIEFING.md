# BRIEFING — 2026-07-07T06:50:00+05:00

## Mission
Execute the Implementation Track for the ERP backend parity & frontend overlapping avatars project.

## 🔒 My Identity
- Archetype: teamwork_preview_implementation_orch
- Roles: orchestrator, user_liaison, human_reporter, successor
- Working directory: /home/xasanboy/ERP/.agents/implementation_orch
- Original parent: main agent
- Original parent conversation ID: f20395c5-8609-4c95-a2d5-a6f529441d94

## 🔒 My Workflow
- **Pattern**: Project
- **Scope document**: /home/xasanboy/ERP/.agents/implementation_orch/SCOPE.md
1. **Decompose**: Decompose implementation into concrete sub-milestones (e.g. Backend Parity checks, Frontend dropdown selection, Frontend avatar stack display) inside SCOPE.md.
2. **Dispatch & Execute**:
   - **Delegate (sub-orchestrator)**: When an item is too large, spawn a sub-orchestrator for it.
   - **Direct (iteration loop)**: For smaller milestones, run Explorer -> Worker -> Reviewer -> Challenger -> Auditor cycle.
3. **On failure** (in this order):
   - Retry: nudge stuck agent or re-send task
   - Replace: spawn fresh agent with partial progress
   - Skip: proceed without (only if non-critical)
   - Redistribute: split stuck agent's remaining work
   - Redesign: re-partition decomposition
   - Escalate: report to parent (sub-orchestrators only, last resort)
4. **Succession**: Self-succeed at 16 spawns, write handoff.md, spawn successor.
- **Work items**:
  1. Backend Verification & Parity [pending]
  2. Frontend Add/Edit Dialogue [pending]
  3. Frontend Avatar Stack [pending]
  4. Phase 1: E2E Test Pass (Tiers 1-4) [pending]
  5. Phase 2: Adversarial Coverage Hardening (Tier 5) [pending]
- **Current phase**: 1
- **Current focus**: Backend Verification & Parity

## 🔒 Key Constraints
- Never reuse a subagent after it has delivered its handoff — always spawn fresh
- All implementations must be genuine (no hardcoding, clean Forensic Auditor verdict)

## Current Parent
- Conversation ID: f20395c5-8609-4c95-a2d5-a6f529441d94
- Updated: not yet

## Key Decisions Made
- Decomposed implementation track into 5 milestones (Backend Parity, Frontend Dialogue, Frontend Avatars, E2E Tiers 1-4, Adversarial Hardening).
- Scheduled heartbeat cron (task-27).

## Team Roster
| Agent | Type | Work Item | Status | Conv ID |
|-------|------|-----------|--------|---------|
| ab88e4bb-ccb3-4008-943c-c2fe882a993f | teamwork_preview_explorer | Explore backend parity and check responsible_user_ids | completed | ab88e4bb-ccb3-4008-943c-c2fe882a993f |
| d038ede1-90bd-4914-b21f-cc5d4093f528 | teamwork_preview_worker | Implement frontend dialog user multiselect and avatar stack | completed | d038ede1-90bd-4914-b21f-cc5d4093f528 |
| 4198731c-24ba-490c-b7e1-f3341c3e82cc | teamwork_preview_worker | Execute E2E tests, fix bugs, and pass 100% of Tiers 1-4 | completed | 4198731c-24ba-490c-b7e1-f3341c3e82cc |
| 581ee264-f30b-44be-943c-c2fe882a993f | teamwork_preview_challenger | White-box adversarial testing (Tier 5) | completed | 581ee264-f30b-44be-9434-5e5c4b602013 |
| 9c1b1bd7-3bc7-4d73-b4da-2ffb3a417a21 | teamwork_preview_challenger | White-box adversarial testing (Tier 5) | completed | 9c1b1bd7-3bc7-4d73-b4da-2ffb3a417a21 |
| 55fbdced-5f57-4d64-9073-290ef800e322 | teamwork_preview_worker | Hardening backend validations, SQLite FK, process start | pending | 55fbdced-5f57-4d64-9073-290ef800e322 |

## Succession Status
- Succession required: no
- Spawn count: 6 / 16
- Pending subagents: [55fbdced-5f57-4d64-9073-290ef800e322]
- Predecessor: none
- Successor: not yet spawned

## Active Timers
- Heartbeat cron: task-27
- Polling cron: task-149
- Safety timer: none
- On succession: kill all timers before spawning successor
- On context truncation: run manage_task(Action="list") — re-create if missing

## Artifact Index
- /home/xasanboy/ERP/.agents/implementation_orch/SCOPE.md — Detailed implementation milestones and statuses
- /home/xasanboy/ERP/.agents/implementation_orch/progress.md — Step-by-step progress tracking and liveness heartbeat
