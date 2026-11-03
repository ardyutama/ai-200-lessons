# AI-200 Prep — 10-Day Plan (Sep 30 → Oct 10, 2026)

Readiness bar ("Solid Practice" in [CONTEXT.md](CONTEXT.md)): every Lab completed unaided at least **once**, weakest-Domain lab re-run after Mock 01, and ≥85% on [Mock 01](mocks/mock-01.md) by Oct 9.

> Revised Oct 6: Labs 03–07 slipped, so the calendar compresses them into Oct 6–8 and Mock 01 moves Oct 7 → Oct 9. Original bar was every Lab twice + Mock by Oct 8.

Ground truth: [AI-200 study guide](https://aka.ms/AI200-StudyGuide) — data 25–30%, the other three Domains 20–25% each. Community intel: [notes/reddit-ai-200-synthesis.md](notes/reddit-ai-200-synthesis.md) (Kubernetes is over-represented; exam format inside).

Daily rhythm: **Anki first (30–45 min cram of due + new cards), then the day's lab/read.** New cards are tagged by Domain so you can Custom-Study `ai200::<domain>` the evening before each lab.

## Calendar

| Day | Work | Artifacts |
|---|---|---|
| **Tue Sep 30** | Run [SETUP.md](SETUP.md) fully. Import/build Anki deck. Cram `ai200::containers`. Read study guide once, end to end. | deck imported |
| **Wed Oct 1** | [Lab 01 — Cosmos DB](labs/01-cosmosdb/README.md). Cram `ai200::data` batch 1. | lab notes |
| **Thu Oct 2** | [Lab 02 — PostgreSQL + pgvector](labs/02-postgres-pgvector/README.md). Cram `ai200::data` batch 2. | lab notes |
| **Fri Oct 3** | [Lab 03 — Managed Redis](labs/03-redis/README.md). Cram `ai200::data` batch 3. Finish all `data` cards. | lab notes |
| **Sat Oct 4** | [Lab 04 — Service Bus](labs/04-service-bus/README.md) + [Lab 05 — Functions](labs/05-functions/README.md). Cram `ai200::integration` (incl. Event Grid theory cards). | lab notes |
| **Sun Oct 5** | [Lab 06 — Key Vault + App Configuration](labs/06-keyvault-appconfig/README.md) + [Lab 07 — OpenTelemetry + KQL](labs/07-otel-kql/README.md). Cram `ai200::ops`. | lab notes |
| **Mon Oct 6** | [Lab 03 — Managed Redis](labs/03-redis/README.md) + [Lab 04 — Service Bus](labs/04-service-bus/README.md). Finish `ai200::data`, start `ai200::integration`. | lab notes |
| **Tue Oct 7** | [Lab 05 — Functions](labs/05-functions/README.md) + [Lab 06 — Key Vault + App Configuration](labs/06-keyvault-appconfig/README.md). Finish `ai200::integration`, start `ai200::ops`. | lab notes |
| **Wed Oct 8** | [Lab 07 — OpenTelemetry + KQL](labs/07-otel-kql/README.md) + [Lab 08 — Kubernetes manifests on kind](labs/08-kubernetes/README.md) **twice** (Reddit's #1 regret). Finish `ai200::ops`, cram `ai200::containers` leftovers (Container Apps/ACR theory). | lab notes |
| **Thu Oct 9** | **Mock 01, timed 100 min** ([mocks/mock-01.md](mocks/mock-01.md)). Grade with the scorecard; every wrong answer → re-read the study-guide bullet → flag related cards. Afternoon: re-run the weakest-Domain lab **unaided**. Evening: [mini-mock](mocks/mini-mock-01.md) (20 q, 30 min) + walk the [exam sandbox](https://aka.ms/examdemo). | scorecard |
| **Fri Oct 10** | **Exam day.** Morning: skim your lab notes + weak cards. No new material. Remember: MS Learn is browsable during the exam; the final Yes/No block has **no review/return**. | 🎯 |

## Anki workflow (10-day cram mode)

Spaced repetition won't mature in 10 days, so run the deck as cram:

1. Study all due/new cards daily.
2. Nightly: Custom Study on the next day's Domain tag (`ai200::data` before Oct 1–3, etc.).
3. From Oct 9 (after Mock 01): filtered deck of cards you lapsed, twice daily.

## Round 2 — Remediation Plan (Oct 11 → Oct 17, 2026)

Attempt 1: **649/1000** on Oct 10. Score report + brain-dump: [notes/exam-attempt-1-braindump.md](notes/exam-attempt-1-braindump.md).

Official top-3 weakest skills (from score report):

1. **Develop event and message-based AI solutions** → [Lab 04 — Service Bus](labs/04-service-bus/README.md) (scaffold-only, never run) + Event Grid (theory-only gap, ADR-0001)
2. **Develop and implement Azure Functions** → [Lab 05 — Functions](labs/05-functions/README.md) (scaffold-only, never run)
3. **Implement container application hosting** → ACR + ACR Tasks + containers on App Service (theory-only gap, ADR-0001). NOT Container Apps ingress — that belongs to the separate "container-orchestrated solutions" skill (official outline, verified 2026-11-03).

Point math: weakest section bar = *Connect to and consume Azure services* (~46%), which is exactly where skills 1–2 live — and both are **lab-able locally** (floci-az covers messaging + functions). Skill 3 is docs + cards. Cheap fix inside the heaviest section (data, 25–30%, bar ~60%): Cosmos DB **indexing policies** deep-read.

Readiness bar for retake: Lab 04 + Lab 05 completed unaided once each, Container Apps + Event Grid card batches at ≥90%, Mock 02 ≥85%.

| Day | Work | Artifacts |
|---|---|---|
| **Sun Oct 11** | [Lab 04 — Service Bus](labs/04-service-bus/README.md) hands-on, full attempt-first. Cram `ai200::integration`. | lab notes |
| **Mon Oct 12** | [Lab 05 — Functions](labs/05-functions/README.md) hands-on, full attempt-first. | lab notes |
| **Tue Oct 13** | Event Grid deep-read (topics, subscriptions, filters, retry/DLQ, Event Grid vs Service Bus decision matrix) → new/sharpened cards. Re-run Lab 05 **unaided**. | cards |
| **Wed Oct 14** | Container Apps hosting + ingress deep-read (internal/external, HTTP/TCP, targetPort, session affinity, CORS, revisions, scaling rules) + ACR theory → cards. Re-run [Lab 08 — Kubernetes](labs/08-kubernetes/README.md) unaided (K8s still over-represented). | cards, lab notes |
| **Thu Oct 15** | Cosmos DB indexing policies deep-read (modes, included/excluded paths, composite, vector index kinds) → cards. Re-run Lab 04 **unaided**. | cards, lab notes |
| **Fri Oct 16** | **Mock 02, timed** (build from attempt-1 weak areas + remediation-mock-01 lapses; include **ordering**, **select-2/select-3**, and **drag-drop matching** formats observed on attempt 1 — see [brain-dump](notes/exam-attempt-1-braindump.md)). Every wrong answer → study-guide bullet → flag cards. Evening: filtered lapse deck + [exam sandbox](https://aka.ms/examdemo) refresher. | scorecard |
| **Sat Oct 17** | **Exam day #2.** Same morning rule: skim lab notes + weak cards only, no new material. Two-pass strategy, lookups only for memorization-shaped facts, 60–90s cap. | 🎯 |

Booking: first retake allowed 24h after attempt 1; book Oct 17 now so the deadline holds.

> **Superseded 2026-11-04:** the Oct 17 sitting never happened. See Round 3 below.

## Round 3 — Retake sprint (Nov 4 → Nov 14, 2026)

New sitting: **Sat 2026-11-14**. Material built 2026-11-03/04; every mock key re-verified against live Microsoft Learn pages:

- 349 new cards appended to the deck (`tag:retake1`; the ten Mock-01 miss-fixers also carry `tag:mock01`) — deck now 576 notes. Drilling menu: [anki/card-index-by-tag.md](anki/card-index-by-tag.md).
- [mocks/mock-02.md](mocks/mock-02.md) — 54 Q, 100 min, bar ≥ 46/54; all formats from attempt 1 (ordering, select-N, matching, dropdown, fill-in, no-return Yes/No).
- [mocks/remediation-mock-02.md](mocks/remediation-mock-02.md) — 30 Q, weak skills only, bar ≥ 26/30.
- [notes/secrets-roles-cheatsheet.md](notes/secrets-roles-cheatsheet.md) — verified RBAC role matrix (control vs data plane).

Deck options: ~12–15 new cards/day, learning steps < 1 day, leech threshold 4; if FSRS is on, desired retention 92–93% and don't re-optimize mid-sprint. Backup before importing the new apkg.

| Day | Work |
|---|---|
| **Wed Nov 5** | New cards: Service Bus / Event Grid / DLQ (`tag:servicebus`, `tag:eventgrid`, `tag:dlq`) |
| **Thu Nov 6** | New cards: Functions incl. Durable (`tag:functions`, `tag:durable`) |
| **Fri Nov 7** | New cards: container hosting — ACR, App Service, sidecars (`tag:acr`, `tag:appservice`, `tag:sidecar`) |
| **Sat Nov 8** | New cards: ACA/KEDA + AKS (`tag:aca`, `tag:keda`, `tag:aks`) |
| **Sun Nov 9** | New cards: Cosmos + pgvector + Redis (`tag:cosmos`, `tag:pgvector`, `tag:redis`) |
| **Mon Nov 10** | New cards: ops sweep (`tag:keyvault`, `tag:appconfig`, `tag:roles`, `tag:otel`, `tag:kql`) |
| **Tue Nov 11** | **Mock 02, timed** → every miss drilled same-day via its weak-skill map |
| **Wed Nov 12** | **Remediation Mock 02** + drill `rated:1:1` + lapsed cards |
| **Thu Nov 13** | Consolidation only — no new cards; filtered lapse deck + [exam sandbox](https://aka.ms/examdemo) refresher |
| **Sat Nov 14** | **Exam day #2.** Morning: skim lab notes + weak cards only, no new material. Two-pass strategy; in-exam Learn lookups only for memorization-shaped facts (roles/limits/SKUs), 60–90s cap, quoted-phrase search. |

## Repo map

- [CONTEXT.md](CONTEXT.md) — glossary (Domain, Card, Lab, Emulator Gap, Mock, Solid Practice)
- [docs/adr/0001](docs/adr/0001-local-only-prep-with-floci-az.md) — why local-only + what the gaps are
- [notes/reddit-ai-200-synthesis.md](notes/reddit-ai-200-synthesis.md) — 7-thread community intel
- [anki/](anki/README.md) — TSV card sources + genanki builder
- [labs/](labs) — 8 hands-on labs mapped to study-guide bullets
- [mocks/](mocks) — timed practice exams
