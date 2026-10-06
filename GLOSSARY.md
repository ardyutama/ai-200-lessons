# Glossary

Domain terms for the AI-200 exam-prep workspace. Definitions only — no implementation detail, no specs.

## Terms

- **Answer key** — A lab's `SOLUTION.md`: the reference solution plus the *why/trap* commentary the exam actually probes. Written to be studied from, then closed.
- **Solid Practice (key-closed run)** — A lab run done with the answer key closed, working from the lab `README.md` alone. Only key-closed runs count toward a lab's "Done when."
- **Case Thread** — The running fictional product (**SupportBrain**) that links labs 02 onward, giving each exercise a shared, realistic motivation. Framing only; it never changes the mandated technology or object names.
- **Azure-side** — Knowledge that cannot be exercised against the local emulator/kind and is therefore learned as say-it-out-loud theory (e.g. AKS provisioning a real Azure Load Balancer). Flagged inline in answer keys.
- **Emulator Gap** — An exam topic the local stand-ins (floci-az, Docker, kind) cannot emulate (Event Grid, Container Apps, ACR, Managed Identity/RBAC, Azure Monitor). Covered by flashcards and guided MS Learn reading only.
- **floci-az** — The local Azure emulator (28 services on `:4577`) standing in for a real Azure subscription, per [ADR 0001](docs/adr/0001-local-only-prep-with-floci-az.md). Uses fixed Azurite-style credentials.
- **kind** — Kubernetes-in-Docker; the local stand-in for AKS. Runs real Kubernetes manifests, but has no cloud provider, so LoadBalancer Services stay `<pending>`.
