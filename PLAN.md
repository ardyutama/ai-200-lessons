# AI-200 Prep — 10-Day Plan (Sep 30 → Oct 10, 2026)

Readiness bar ("Solid Practice" in [CONTEXT.md](CONTEXT.md)): every Lab completed unaided **twice**, and ≥85% on [Mock 01](mocks/mock-01.md) by Oct 8.

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
| **Mon Oct 6** | [Lab 08 — Kubernetes manifests on kind](labs/08-kubernetes/README.md) (do it twice — Reddit's #1 regret). Cram `ai200::containers` leftovers (Container Apps/ACR theory). | lab notes |
| **Tue Oct 7** | **Mock 01, timed 100 min** ([mocks/mock-01.md](mocks/mock-01.md)). Grade with the scorecard; every wrong answer → re-read the study-guide bullet → flag related cards. | scorecard |
| **Wed Oct 8** | Re-run the two weakest-Domain labs **unaided**. Targeted card cram of weak tags. Decision point from [ADR-0001](docs/adr/0001-local-only-prep-with-floci-az.md): if `ops` < target, reconsider a free subscription. | 2nd-pass labs |
| **Thu Oct 9** | [Mini-mock](mocks/mini-mock-01.md) (20 q, 30 min). Walk the [exam sandbox](https://aka.ms/examdemo) so the UI is familiar. Light cards only in the evening. | mini-mock score |
| **Fri Oct 10** | **Exam day.** Morning: skim your lab notes + weak cards. No new material. Remember: MS Learn is browsable during the exam; the final Yes/No block has **no review/return**. | 🎯 |

## Anki workflow (10-day cram mode)

Spaced repetition won't mature in 10 days, so run the deck as cram:

1. Study all due/new cards daily.
2. Nightly: Custom Study on the next day's Domain tag (`ai200::data` before Oct 1–3, etc.).
3. From Oct 7: filtered deck of cards you lapsed, twice daily.

## Repo map

- [CONTEXT.md](CONTEXT.md) — glossary (Domain, Card, Lab, Emulator Gap, Mock, Solid Practice)
- [docs/adr/0001](docs/adr/0001-local-only-prep-with-floci-az.md) — why local-only + what the gaps are
- [notes/reddit-ai-200-synthesis.md](notes/reddit-ai-200-synthesis.md) — 7-thread community intel
- [anki/](anki/README.md) — TSV card sources + genanki builder
- [labs/](labs) — 8 hands-on labs mapped to study-guide bullets
- [mocks/](mocks) — timed practice exams
