# AI-200 Exam Prep

Glossary for a 10-day preparation project targeting Microsoft Exam AI-200 (Azure AI Cloud Developer Associate). Exam date: 2026-10-10.

## Language

**Exam**:
Microsoft Exam AI-200, "Developing AI Cloud Solutions on Azure". Grants the Microsoft Certified: Azure AI Cloud Developer Associate credential. 120 minutes, proctored, passing score 700/1000. Source of truth: aka.ms/AI200-StudyGuide.
_Avoid_: certification (that is the credential, not the exam), AI-200T00 (that is the course)

**Course**:
AI-200T00-A, the 5-day Microsoft Learn course aligned to the Exam; 9 self-paced modules. Source material for notes and Cards.
_Avoid_: learning path, lessons

**Domain**:
One of the four weighted skill areas from the official study guide, used as the organizing unit for Cards, Labs, and Mocks: `containers` (20–25%), `data` (25–30%), `integration` (20–25%), `ops` (20–25%).
_Avoid_: module, section, topic

**Card**:
A single Anki flashcard, authored as TSV in `anki/` and tagged by Domain (`ai200::containers`, `ai200::data`, `ai200::integration`, `ai200::ops`). Types: basic, cloze, scenario.
_Avoid_: note (Anki-internal term), question (that is Mock territory)

**Lab**:
A hands-on exercise in `labs/` that runs entirely locally — against floci-az or another local runtime — and is completable without an Azure subscription.
_Avoid_: tutorial, walkthrough, exercise

**Solution**:
The answer key for a Lab, in `labs/<lab>/SOLUTION.md`. Each Lab step is rephrased as an exam-style question, followed by the answer, a runnable per-step snippet, and a why/trap note. A Lab's first pass may consult its Solution; the two runs counted toward Solid Practice must be done with it closed.
_Avoid_: answer sheet, cheat sheet

**Case Thread**:
A single running scenario carried through every block of a Solution, so snippets read as one realistic job rather than isolated demos (Lab 02: SupportBrain, a multi-tenant support-docs RAG for tenants `contoso`/`fabrikam`). Device exists to anchor recall; reuse across Solutions when it fits.
_Avoid_: narrative, story mode

**floci-az**:
The local Azure emulator (28 services, port 4577) used as the zero-cost Azure stand-in for Labs. Covers: Blob, Cosmos DB, PostgreSQL, Redis, Service Bus, Event Hubs, Functions, Key Vault, App Configuration, AKS (control-plane).

**Emulator Gap**:
An Exam topic that cannot be run locally: Event Grid, Container Apps, Azure Container Registry, Managed Identity/RBAC, Azure Monitor/Application Insights. Covered by Cards and guided MS Learn reading only.
_Avoid_: weakness, blind spot

**Mock**:
A timed practice exam in `mocks/`, generated from the study guide and mirroring the reported real-exam format (case studies, dropdown/select-value items, a no-review Yes/No section).
_Avoid_: practice test dump, cheat sheet

**Solid Practice**:
The agreed readiness bar: every Lab completed unaided twice, and ≥85% on the Mock by 2026-10-08.
_Avoid_: "feeling ready", done
