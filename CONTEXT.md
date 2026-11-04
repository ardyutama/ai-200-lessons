# AI-200 Exam Prep

Glossary for the preparation project targeting Microsoft Exam AI-200 (Azure AI Cloud Developer Associate). Attempt 1: 2026-10-10 (649/1000, fail — brain-dump in notes/). Retake: 2026-11-14.

## Language

### Exam and skills

**Exam**:
Microsoft Exam AI-200, "Developing AI Cloud Solutions on Azure". Grants the Microsoft Certified: Azure AI Cloud Developer Associate credential. 120 minutes, proctored, passing score 700/1000. Source of truth: aka.ms/AI200-StudyGuide.
_Avoid_: certification (that is the credential, not the exam), AI-200T00 (that is the course)

**Course**:
AI-200T00-A, the 5-day Microsoft Learn course aligned to the Exam; 9 self-paced modules. Source material for the deck and for the study write-ups in `notes/`.
_Avoid_: learning path, lessons

**Domain**:
One of the four weighted skill areas from the official study guide, used as the organizing unit for Notes, Labs, and Mocks: `containers` (20–25%), `data` (25–30%), `integration` (20–25%), `ops` (20–25%). (Data briefly read 30–35% in Oct 2026; the live study guide reverted — re-check aka.ms/AI200-StudyGuide before the sitting.)
_Avoid_: module, section, topic

**Weak skill**:
One of the three study-guide skills the attempt-1 score report flagged as top priority: (a) event- and message-based solutions, (b) Azure Functions, (c) container application hosting (ACR, ACR Tasks, App Service).
_Avoid_: weak area, weak domain

### Deck

**Note**:
One authored flashcard source: a row in the deck's TSV files in `anki/` (basic or cloze), tagged by Domain (`ai200::containers`, `ai200::data`, `ai200::integration`, `ai200::ops`). Its identity follows its text, so editing the text creates a new Note in Anki. Not the study write-ups in `notes/`.
_Avoid_: card (for the TSV row)

**Card**:
One reviewable item in Anki, generated from a Note: one for a basic Note, one per cloze number for a cloze Note. Daily new-card limits and due counts are measured in Cards.
_Avoid_: question (that is Mock territory)

**Retake batch**:
The Notes added for the 2026-11-14 retake, tagged `retake1` and written as ten topic batches in weak-skill-first order; the ten Mock-01 miss-fixers also carry `mock01`.
_Avoid_: round-3 pack (it also includes Mocks)

**Orphan**:
A Note left in the Anki collection after its source row was edited or removed. Deleted by hand; the edited text arrives as a new Note.

### Practice

**Lab**:
A hands-on exercise in `labs/` that runs entirely locally — against floci-az or another local runtime — and is completable without an Azure subscription.
_Avoid_: tutorial, walkthrough, exercise

**Solution**:
The answer key for a Lab, in `labs/<lab>/SOLUTION.md`. Each Lab step is rephrased as an exam-style question, followed by the answer, a runnable per-step snippet, and a why/trap note. A Lab's first pass may consult its Solution.
_Avoid_: answer key (reserved for a Mock's grading section), answer sheet, cheat sheet

**Key-closed run**:
A Lab run done with its Solution closed, working from the Lab's README alone. Only Key-closed runs count toward a Lab's "Done when" and toward Solid Practice.

**Case Thread**:
A single running scenario carried through every block of a Solution and the case-study sections of Mocks, so snippets read as one realistic job rather than isolated demos (SupportBrain, a multi-tenant support-docs RAG for tenants `contoso`/`fabrikam`, from Lab 02 onward). Framing only: it never changes the mandated technology or object names.
_Avoid_: narrative, story mode

**Mock**:
A timed practice exam in `mocks/`, generated from the study guide and mirroring the reported real-exam format (case studies, dropdown/select-value items, a no-review Yes/No section).
_Avoid_: practice test dump, cheat sheet

**Remediation Mock**:
A short Mock aimed at the Weak skills, taken after a full Mock to check they are fixed, with a pass bar at least as high as the full Mock's.

**Solid Practice**:
The readiness bar for sitting the Exam: Key-closed runs of the Labs plus at least 85% on a Mock. PLAN.md sets the exact counts and dates per round.
_Avoid_: "feeling ready", done

### Environment

**floci-az**:
The local Azure emulator (28 services, port 4577) used as the zero-cost Azure stand-in for Labs. Covers: Blob, Cosmos DB, PostgreSQL, Redis, Service Bus, Event Hubs, Functions, Key Vault, App Configuration, AKS (control-plane).

**kind**:
Kubernetes-in-Docker, the local stand-in for AKS. It runs real manifests but has no cloud provider, so LoadBalancer Services stay pending.

**Emulator Gap**:
An Exam topic the local stand-ins (floci-az, Docker, kind) cannot run: Event Grid, Container Apps, Azure Container Registry, Managed Identity/RBAC, Azure Monitor/Application Insights. Covered by Cards and guided MS Learn reading only.
_Avoid_: weakness, blind spot

**Azure-side**:
A fact inside an otherwise runnable Lab that the local stand-ins cannot exercise (e.g. AKS provisioning a real Azure Load Balancer). Learned as say-it-out-loud theory and flagged inline in the Solution.
