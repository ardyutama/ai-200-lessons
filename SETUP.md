# Setup Guide — AI-200 local prep environment

Everything below is for you to run (macOS, Homebrew already present). Nothing here touches a real Azure account.

## 1. Core tools

```bash
# floci CLI (manages the floci-az Azure emulator)
brew install floci-io/floci/floci

# Azure CLI (used against floci-az endpoints)
brew install azure-cli

# kind — local Kubernetes for the AKS/manifests lab
brew install kind

# Python deps (isolated venv in this repo)
cd ~/Documents/personal/ai-200-lessons
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install \
  azure-cosmos \
  azure-servicebus \
  azure-storage-blob \
  azure-keyvault-secrets \
  azure-appconfiguration \
  azure-identity \
  psycopg[binary] \
  redis \
  opentelemetry-sdk \
  opentelemetry-exporter-otlp-proto-http \
  genanki
```

## 2. Start the local Azure (floci-az)

```bash
floci az start          # 28 services on :4577, AMQP on :5672/:5673
eval $(floci az env)    # loads AZURE_STORAGE_CONNECTION_STRING etc.
floci az doctor         # sanity check
```

Fixed dev credentials (Azurite-compatible): account `devstoreaccount1`, endpoints `http://localhost:4577/devstoreaccount1`.

Stop/reset: `floci az stop` (state is disposable — restart gives a clean cloud; use `floci az start --persist ./data` if you want state to survive).

## 3. Local runtimes for emulator gaps (Docker, already installed)

```bash
# PostgreSQL with pgvector (Lab 02)
docker run -d --name pgvec -e POSTGRES_PASSWORD=postgres -p 5432:5432 pgvector/pgvector:pg16

# Jaeger for OpenTelemetry traces (Lab 07)
docker run -d --name jaeger -p 16686:16686 -p 4318:4318 jaegertracing/all-in-one:latest

# Kusto (Azure Data Explorer) emulator for KQL practice (Lab 07) — ~2 GB, runs under Rosetta on Apple Silicon
docker run -d --name kustainer -e ACCEPT_EULA=Y -p 8080:8080 mcr.microsoft.com/azuredataexplorer/kustainer-linux:latest
```

## 4. Kubernetes (Lab 08)

```bash
kind create cluster --name ai200
kubectl cluster-info
# teardown: kind delete cluster --name ai200
```

## 5. Anki deck import (or build .apkg)

Zero-tooling path: Anki → File → Import → pick the TSVs in `anki/`, map columns per [anki/README.md](anki/README.md).

Nicer path (proper note types + tags baked in):

```bash
source .venv/bin/activate
python anki/build_apkg.py   # writes anki/AI-200.apkg — double-click to import
```

## Verify you're ready

```bash
floci az status && echo FLOCI-OK
docker ps --format '{{.Names}}' | grep -E 'pgvec|jaeger|kustainer'
kind get clusters | grep ai200
source .venv/bin/activate && python -c "import azure.cosmos, azure.servicebus, genanki; print('PY-OK')"
```
