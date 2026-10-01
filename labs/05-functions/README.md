# Lab 05 — Azure Functions

**Study-guide bullets covered:** serverless APIs with triggers and bindings · configure and deploy function apps.

**Setup:** `brew tap azure/functions && brew install azure-functions-core-tools@4` (from [SETUP.md](../../SETUP.md)). floci-az is Azurite-compatible, so `local.settings.json` can point at the floci-az storage connection string.

## Steps

1. **Scaffold.** `func init funcs --python -m V2` then `cd funcs && func new --template "HTTP trigger" --name hello`. Inspect `function_app.py`: note the v2 decorator model and the `auth_level`.
2. **Run locally.** `func start` → curl the endpoint. Test the key behavior: set `auth_level=ANONYMOUS` vs `FUNCTION` and observe the `?code=` requirement.
3. **Timer trigger.** Add a timer function with `0 */1 * * * *` (every minute, 6-field NCRONTAB). Watch it fire; explain each field and the UTC default.
4. **Service Bus integration.** With Lab 04's queue up, add `@app.service_bus_queue_trigger(arg_name="msg", queue_name="jobs", connection="SB_CONN")` and log the body. Explain auto-complete on success / abandon on exception, and how the retry policy in `host.json` interacts with MaxDeliveryCount.
5. **Output binding.** Add a queue **output** binding (`@app.queue_output`) so the HTTP trigger enqueues a message without SDK code. Triggers = 1 per function; bindings = declarative I/O.
6. **Deploy knowledge.** You can't deploy to real Azure (ADR-0001), but recite it: `func azure functionapp publish <app>` (zip deploy), app settings move to Function App settings / Key Vault references, plans: Consumption vs Premium vs Dedicated (cold start!).

## Done when

- [ ] HTTP + timer + Service Bus functions all run locally
- [ ] You can recite the v2 decorators and what host.json vs local.settings.json control
- [ ] You can explain when the exam wants Premium (cold start / VNet)

## Cleanup

Ctrl+C the host; `floci az stop` when done.
