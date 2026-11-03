# Browsing Microsoft Learn during the exam (fetched 2026-10-09)

How to use the in-exam Microsoft Learn browser efficiently on a role-based exam (AI-200 is one). OFFICIAL claims are from Microsoft's exam-experience doc; COMMUNITY claims are from r/AzureCertification threads and are not officially guaranteed. Fetched the night before exam day (2026-10-10) because Reddit access required a real browser session.

## Official rules of the in-exam Learn browser

Source: [Exam duration and exam experience — Microsoft Learn](https://learn.microsoft.com/en-us/credentials/support/exam-duration-exam-experience) (section "Accessing Microsoft Learn during your certification exam").

- Available on **associate/expert role-based exams only** — NOT Fundamentals, GitHub, or MOS exams. AI-200 qualifies.
- You get the **whole learn.microsoft.com domain except Q&A, Practice Assessments, and your profile** (no sign-in).
- **No extra time is added; the exam timer keeps running** while you browse.
- Microsoft explicitly warns it is **not for answering every question**: "If you do, you won't be able to complete the exam in the time allotted, and that is by design."
- Opened via a **Microsoft Learn button in the left nav pane** → opens split-screen right of the question; a splitter resizes; can go full-screen (timer + question count stay visible in the header).
- **Multiple tabs** of Learn can be open and individually closed.
- **Browsing is restricted to the learn.microsoft.com domain** — external links (e.g. GitHub) show a "blocked" message.
- **Ctrl+F / Cmd+F works inside the current Learn page** (highlights matches, Next/Previous arrows). It does NOT work in the exam window, and **closing the Learn window resets your search history**.
- Same languages as the exam. Official demo of the exam UI: [exam sandbox](https://aka.ms/examdemo).

## Community-reported experience (r/AzureCertification)

Sources: [How much of Microsoft Learn is "acceptable" in exams?](https://www.reddit.com/r/AzureCertification/comments/1qwjd6y/) · [Wdym by querying Microsoft Learn during exams?](https://www.reddit.com/r/AzureCertification/comments/1u3y9sn/) (both fetched 2026-10-09).

- **Everything visible in the in-exam browser is permitted** — no need to self-censor pages; Q&A and external links are blocked for you. "It's not cheating if Microsoft allows it."
- **Best-use pattern: answer from knowledge first, then spend leftover time** verifying low-confidence answers (MD-102 taker). An AZ-104 taker estimates AI/keyword lookups rescued **4–5 questions**, and that 10 spare minutes could have confirmed 5–6 more.
- **Time is the real constraint.** That same AZ-104 taker still ran out of time and failed (660) — his mistake was over-budgeting scenario questions, then relying on lookups. "Time becomes a bigger issue on harder exams."
- **Search quality is mediocre** (Bing-backed; "mostly terrible" per one taker). Very specific items (exact SKUs) are hard to find — facts are "compiled and buried in tables."
- **Keyword syntax that works**: `"quoted phrase"` for exact matches, `+` to combine multiple keywords.
- **Copilot/AI answers inside Learn search are inconsistent**: one taker used them heavily ("really good"), another reports the AI "cannot ask complex things, it is disabled", and a third says it appears on some topics but often returns no summary. **Do not depend on it.**
- **Courses/Training/Docs tabs are reachable** (community), consistent with the official "whole domain minus Q&A/Practice Assessments/profile" rule. Note: Practice Assessments specifically ARE blocked (official).
- Works at **Pearson VUE test centers** as well as online-proctored (OnVUE) sessions (community).
- Study-guide pages themselves can surface in search results (MD-102 taker) — allowed, since only Q&A/assessments/profile are excluded.

## Efficient browsing techniques (synthesis)

1. **Two-pass strategy**: first pass answer everything from knowledge and flag shaky items; second pass = targeted lookups only. Never browse mid-flow on a question you could have answered.
2. **Lookup targets = memorization-shaped facts**: limits, defaults, role/permission names, SKU/tier names, config keys, CLI flag names. Community confirms permission/role questions were the best ROI (SC-200, AZ-104).
3. **Use `"quotes"` and `+`** in Learn search; skip natural-language questions.
4. **Once on the right page, Cmd+F** to jump to the term — but remember closing the Learn window wipes search state (official), so keep it open between related lookups.
5. **Open a tab per topic** when cross-checking several facts (official multi-tab support).
6. **Don't chase exact SKUs or tables longer than ~60–90 seconds** — community consensus is that deep hunting loses more points than it wins.
7. **Treat AI summaries as a bonus, never the plan** — availability varies by topic and exam.

## Traps

- Timer never pauses; no extra time (official).
- Using Learn for every question guarantees not finishing — "by design" (official).
- GitHub and all non-Learn domains blocked (official) — no GitHub-hosted samples, no Stack Overflow.
- Q&A and Practice Assessments blocked (official); don't burn time looking for them.
- Learn window close = search history reset (official).

## Pre-exam drill (tonight, ~20 min)

Practice timed lookups on learn.microsoft.com against this repo's weakest links, using the real search syntax:

- Cosmos DB: vector policy / `VectorIndex` kinds, consistency levels
- PostgreSQL pgvector: IVFFlat `lists`/`probes`, HNSW params
- Redis: `FT.CREATE` schema field types (TAG vs TEXT), eviction policies
- Service Bus: message settlement modes, duplicate detection window
- Functions: binding expressions, trigger scaling rules
- Key Vault vs App Configuration: which stores what
- KQL: `summarize`, `bin()`, `render` operators
- AKS/Kubernetes: Deployment vs Service manifest fields (Reddit says K8s is over-represented)

Then walk the [exam sandbox](https://aka.ms/examdemo) so the split-screen Learn button and the no-return Yes/No block are familiar.
