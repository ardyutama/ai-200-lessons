# 0001. Local-only exam prep on floci-az (no Azure subscription)

**Status**: accepted (2026-09-30)

The candidate has no Azure subscription and a 10-day runway to Exam AI-200. We decided that all hands-on practice runs locally: floci-az (28 emulated Azure services on :4577) as the Azure stand-in, plus local runtimes for what floci-az cannot emulate (Docker/kind for Kubernetes manifests, Jaeger for OpenTelemetry). Emulator Gaps (Event Grid, Container Apps, ACR, Managed Identity/RBAC, Azure Monitor) are covered by Cards and guided MS Learn reading only.

**Considered options**: (a) create a free Azure subscription for the gap topics — rejected, user declined; (b) cards-only prep with no labs — rejected, the Exam rewards hands-on fluency and Reddit pass reports stress exercises; (c) local-only with theory cards for gaps — chosen.

**Consequences**: identity/RBAC and Azure Monitor questions are the highest-risk exam areas; if the Mock shows the `ops` Domain below target, reconsider a throwaway free subscription in the final week. floci-az uses fixed Azurite-style credentials, so all Labs must use connection-string auth patterns — Managed Identity code paths are studied as theory only.
