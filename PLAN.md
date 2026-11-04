# AI-200 Prep — 10-Day Plan (Sep 30 → Oct 10, 2026)

Readiness bar ("Solid Practice" in [CONTEXT.md](CONTEXT.md)): every Lab completed unaided at least **once**, weakest-Domain lab re-run after Mock 01, and ≥85% on [Mock 01](mocks/mock-01.md) by Oct 9.

> Revised Oct 6: Labs 03–07 slipped, so the calendar compresses them into Oct 6–8 and Mock 01 moves Oct 7 → Oct 9. Original bar was every Lab twice + Mock by Oct 8.

Ground truth: [AI-200 study guide](https://aka.ms/AI200-StudyGuide) — data 25–30%, the other three Domains 20–25% each. Community intel: [notes/reddit-ai-200-synthesis.md](notes/reddit-ai-200-synthesis.md) (Kubernetes is over-represented; exam format inside).

Daily rhythm: **Anki first (30–45 min cram of due + new cards), then the day's lab/read.** New cards are tagged by Domain so you can Custom-Study `ai200::<domain>` the evening before each lab.

## Calendar

| Day | Work | Artifacts |
|---|---|---|
| **Wed Sep 30** | Run [SETUP.md](SETUP.md) fully. Import/build Anki deck. Cram `ai200::containers`. Read study guide once, end to end. | deck imported |
| **Thu Oct 1** | [Lab 01 — Cosmos DB](labs/01-cosmosdb/README.md). Cram `ai200::data` batch 1. | lab notes |
| **Fri Oct 2** | [Lab 02 — PostgreSQL + pgvector](labs/02-postgres-pgvector/README.md). Cram `ai200::data` batch 2. | lab notes |
| **Sat Oct 3** | [Lab 03 — Managed Redis](labs/03-redis/README.md). Cram `ai200::data` batch 3. Finish all `data` cards. | lab notes |
| **Sun Oct 4** | [Lab 04 — Service Bus](labs/04-service-bus/README.md) + [Lab 05 — Functions](labs/05-functions/README.md). Cram `ai200::integration` (incl. Event Grid theory cards). | lab notes |
| **Mon Oct 5** | [Lab 06 — Key Vault + App Configuration](labs/06-keyvault-appconfig/README.md) + [Lab 07 — OpenTelemetry + KQL](labs/07-otel-kql/README.md). Cram `ai200::ops`. | lab notes |
| **Tue Oct 6** | [Lab 03 — Managed Redis](labs/03-redis/README.md) + [Lab 04 — Service Bus](labs/04-service-bus/README.md). Finish `ai200::data`, start `ai200::integration`. | lab notes |
| **Wed Oct 7** | [Lab 05 — Functions](labs/05-functions/README.md) + [Lab 06 — Key Vault + App Configuration](labs/06-keyvault-appconfig/README.md). Finish `ai200::integration`, start `ai200::ops`. | lab notes |
| **Thu Oct 8** | [Lab 07 — OpenTelemetry + KQL](labs/07-otel-kql/README.md) + [Lab 08 — Kubernetes manifests on kind](labs/08-kubernetes/README.md) **twice** (Reddit's #1 regret). Finish `ai200::ops`, cram `ai200::containers` leftovers (Container Apps/ACR theory). | lab notes |
| **Fri Oct 9** | **Mock 01, timed 100 min** ([mocks/mock-01.md](mocks/mock-01.md)). Grade with the scorecard; every wrong answer → re-read the study-guide bullet → flag related cards. Afternoon: re-run the weakest-Domain lab **unaided**. Evening: [mini-mock](mocks/mini-mock-01.md) (20 q, 30 min) + walk the [exam sandbox](https://aka.ms/examdemo). | scorecard |
| **Sat Oct 10** | **Exam day.** Morning: skim your lab notes + weak cards. No new material. Remember: MS Learn is browsable during the exam; the final Yes/No block has **no review/return**. | 🎯 |

## Anki workflow (10-day cram mode)

Spaced repetition won't mature in 10 days, so run the deck as cram:

1. Study all due/new cards daily.
2. Nightly: Custom Study on the next day's Domain tag (`ai200::data` before Oct 1–3, etc.).
3. From Oct 9 (after Mock 01): filtered deck of cards you lapsed, twice daily.

> Round 3 replaces this with the filtered-deck intake described there.

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

Sitting: **Sat 2026-11-14, 11:00 WITA, online** (booked). Decision: sit regardless of mock scores; the mock bars below are drill targets, not gates. Free reschedule/cancel closes 24 h before the start (Fri Nov 13, 11:00 WITA), and a failed attempt means a 14-day wait ([Microsoft Learn policies](https://learn.microsoft.com/en-us/credentials/support/retake-policy)).

Budget: 2 h/day on Nov 5–10, about 3 h on Wed Nov 11. Weak skills first (Days 1–3); Days 4–6 are "if time allows". Round 3 bar (advisory): one Key-closed run each of Lab 04 and Lab 05, Mock 02 ≥ 46/54, Remediation Mock 02 ≥ 26/30. Both labs were scaffold-only in Round 2 (never run), so their first run can overrun: keep the Cards and cut the lab to steps 1–4 (Lab 04) or 1, 2, 4 (Lab 05).

Material built 2026-11-03/04; every mock key re-verified against live Microsoft Learn pages:

- 349 new Notes (385 Cards) appended to the deck (`tag:retake1`; the ten Mock-01 miss-fixers also carry `tag:mock01`) — deck now 576 Notes (624 Cards). Every Note carries a sprint-day tag, so the day searches below reach all of them. Drilling menu: [anki/card-index-by-tag.md](anki/card-index-by-tag.md).
- [mocks/mock-02.md](mocks/mock-02.md) — 54 Q, 100 min, target ≥ 46/54; all formats from attempt 1 (ordering, select-N, matching, dropdown, fill-in, no-return Yes/No).
- [mocks/remediation-mock-02.md](mocks/remediation-mock-02.md) — 30 Q, Weak skills only, target ≥ 26/30.
- [notes/secrets-roles-cheatsheet.md](notes/secrets-roles-cheatsheet.md) — verified RBAC role matrix (control vs data plane).

**Intake.** Each day starts with one filtered deck (Tools → Create Filtered Deck, or Custom Study → Study by card state or tag): search `deck:AI-200 tag:retake1 is:new (` + every tag listed up to that day + `)`, order *Order added*, card limit as in the table. Ready-made strings are in the Sprint days table of [anki/card-index-by-tag.md](anki/card-index-by-tag.md). `is:new` rolls leftovers forward when you rebuild; empty the filtered deck at the end of the day. The home deck stays at about 15 new/day as a background trickle for whatever Days 4–6 don't reach.

Deck options: learning steps under 1 day, leech threshold 4; if FSRS is on, desired retention 92–93% and don't re-optimize mid-sprint. Back up before importing the new apkg (checklist in [anki/README.md](anki/README.md)).

| Day | Work | Filtered deck |
|---|---|---|
| **Thu Nov 5** | Weak skill (a), Service Bus / Event Grid / DLQ: Cards first, then **Lab 04** Key-closed run (floci-az, steps 1–4 from the README alone) and a skim of the Event Grid vs Service Bus vs Event Hubs decision guide | limit 54 · adds `servicebus`, `eventgrid`, `dlq` |
| **Fri Nov 6** | Weak skill (b), Functions incl. Durable: Cards first, then **Lab 05** Key-closed run (Lab 04's queue must be up for step 4) | limit 54 · adds `functions`, `durable` |
| **Sat Nov 7** | Weak skill (c), container hosting: Cards first, then Learn reading on ACR auth, ACR Tasks and App Service custom-container/sidecar settings (Emulator Gap: theory only) | limit 54 · adds `acr`, `appservice`, `sidecar` |
| **Sun Nov 8** | If time allows: ACA/KEDA + AKS Cards, then re-drill [mini-mock-01](mocks/mini-mock-01.md) (20 Q, 30 min) | limit 60 · adds `aca`, `keda`, `aks` |
| **Mon Nov 9** | If time allows: Cosmos + pgvector + Redis Cards, then re-drill [remediation-mock-01](mocks/remediation-mock-01.md) (30 Q, 45 min) | limit 60 · adds `cosmos`, `pgvector`, `redis` |
| **Tue Nov 10** | If time allows: ops sweep Cards, then re-do only the questions missed in the two re-drills | limit 60 · adds `keyvault`, `appconfig`, `roles`, `otel`, `kql` |
| **Wed Nov 11** | **Mock 02, timed** (about 3 h with the same-day drill) → every miss drilled via its weak-skill map | — |
| **Thu Nov 12** | **Remediation Mock 02** + drill `rated:1:1` + lapsed Cards | — |
| **Fri Nov 13** | Consolidation only — no new Cards; filtered lapse deck + [exam sandbox](https://aka.ms/examdemo) refresher. Last free reschedule point is 11:00 WITA (decision: sit regardless) | — |
| **Sat Nov 14** | **Exam day #2, 11:00 WITA online.** Morning: skim lab notes + weak Cards only, no new material. Two-pass strategy; in-exam Learn lookups only for memorization-shaped facts (roles/limits/SKUs), 60–90s cap, quoted-phrase search. | — |

## Repo map

- [CONTEXT.md](CONTEXT.md) — glossary (Domain, Weak skill, Note, Card, Lab, Mock, Solid Practice, Emulator Gap)
- [docs/adr/0001](docs/adr/0001-local-only-prep-with-floci-az.md) — why local-only + what the gaps are
- [docs/adr/0002](docs/adr/0002-content-derived-note-identity.md) — why editing a Note's text creates a new Note (Orphans)
- [notes/reddit-ai-200-synthesis.md](notes/reddit-ai-200-synthesis.md) — 7-thread community intel
- [anki/](anki/README.md) — TSV card sources + genanki builder
- [labs/](labs) — 8 hands-on labs mapped to study-guide bullets
- [mocks/](mocks) — timed practice exams
