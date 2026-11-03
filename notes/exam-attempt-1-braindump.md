# Exam attempt 1 — brain-dump (2026-10-10, same day as exam)

Score: **649 / 1000** (700 to pass). Captured same-day while memory is fresh.

## Self-reported weak areas (user's words)

1. **Azure Functions — "most of all, a lot"** → biggest bleed.
2. **Cosmos DB — indexing policies** (specific, memorization-shaped).
3. **Ingress settings for apps** → Container Apps ingress config.

## Mapping to repo state

| Weak area | Prep status going in | Verdict |
|---|---|---|
| Azure Functions | [labs/05-functions](../labs/05-functions/) = scaffold only (README, no SOLUTION.md) — never went hands-on | Predicted gap, confirmed |
| Cosmos DB indexing policies | Lab 01 done, but indexing policy = theory/card territory, not exercised in lab | Depth gap inside a "done" domain |
| Container Apps ingress | Known no-lab gap (ADR-0001) — theory-only, cards only | Calculated risk, confirmed |

## Pattern

2 of 3 weak areas were **known theory-only domains** (Container Apps) or **scaffolded-but-never-run labs** (Functions). The third (indexing policies) is a memorization-shaped subtopic inside a labbed domain — exactly the kind of fact the in-exam Learn lookup is for, per [ms-learn-browsing-during-exam.md](ms-learn-browsing-during-exam.md).

## Question formats observed (attempt 1)

Beyond the known format (≈5 case-study + 49 mixed + 4 no-return Yes/No), the mixed section included:

- **Ordering questions** — arrange steps in the correct sequence (drag-order style).
- **"Select 3"** — multi-select exactly 3 options.
- **"Select 2"** — multi-select exactly 2 options.
- **Matching / drag-and-drop** — e.g. "which role fits this scenario", drag role names onto descriptions from a shared option pool (options may be usable more than once or not at all — read the instruction line).

Implication for Mock 02: must include ordering + select-N + matching items, not just single-answer MCQ — these formats punish partial knowledge differently (an ordering question is all-or-nothing unless scored per-position; select-N has no partial credit signal in the report). Matching questions on **roles/permissions** are memorization-shaped = prime in-exam Learn lookup targets (60–90s cap still applies).

Ordering-question tactics for round 2: anchor the **first and last** step first, then eliminate impossible adjacencies; provision/configure steps almost always follow create-resource steps; "secure it" (identity, keys, firewall) comes after "it exists and works."

## Official score report (received same day)

Section bars (approx., shorter = weaker):

| Section (weight) | Bar | Note |
|---|---|---|
| Containerized solutions (20–25%) | ~60% | mid |
| Data management services (30–35%) | ~60% | mid — **heaviest section** |
| **Connect to and consume Azure services (20–25%)** | **~46%** | **weakest bar** — Functions + event/message live here |
| Secure, monitor, troubleshoot (20–25%) | ~68% | strongest |

Microsoft's top-3 priority skills: **Develop event and message-based AI solutions** · **Develop and implement Azure Functions** · **Implement container application hosting**. Matches the self-report (Functions, ingress) and adds Service Bus/Event Grid (lab 04 scaffold-only + Event Grid theory-gap — predicted).

## Resolution

- [x] Official score report domain breakdown — received, table above.
- [x] Round-2 plan built into [PLAN.md](../PLAN.md) — retake Sat Oct 17, 2026. Priorities: Lab 04 + Lab 05 hands-on (both lab-able via floci-az), Container Apps ingress + Event Grid docs/cards, Cosmos indexing policies.
