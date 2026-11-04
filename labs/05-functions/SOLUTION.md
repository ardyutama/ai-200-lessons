# Solution 05 — Azure Functions (answer key)

> **Attempt-first rule.** First pass: you may consult this key. The two runs that count toward *Solid Practice* must be done with this file **closed**. When you're ready for a counted run, close it and work from [README.md](README.md) alone.

**The Case Thread.** SupportBrain's ingestion runs as one Function App. An HTTP endpoint accepts an article and queues it for indexing, a Service Bus trigger embeds each job from Lab 04's `jobs` queue, and a timer sweeps stuck work every minute. Every block below is the next thing you do on that app.

**Setup (do once):**

```bash
brew tap azure/functions && brew install azure-functions-core-tools@4   # not installed on this machine yet
func init funcs --python -m V2
cd funcs && func new --template "HTTP trigger" --name hello
```

Core Tools writes `funcs/requirements.txt` with `azure-functions` and builds the app's own virtual environment. The repo `.venv` is not used in this lab. Paste the blocks into `funcs/function_app.py`, one app, top to bottom.

> **Note on the runtime split.** Core Tools runs the Functions host locally. Storage-based bindings use the floci-az storage connection, which is Azurite-compatible (README). The Service Bus trigger reads Lab 04's `jobs` queue. Anything marked **Azure-side** is say-it-out-loud knowledge.

> **Verification status (2026-11-04).** Decorator names, the host.json key, and the local-settings rules were checked against Microsoft Learn. Core Tools and `azure-functions` are not installed here, so nothing in this file has been run. `func start` is the first real test.

---

## Block 1 — The v2 decorator model (HTTP trigger)

**Q.** Write an HTTP-triggered function with the Python v2 model. Where does the auth level live, and what does a caller need to send?

```python
import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="hello", methods=["GET"])
def hello(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(f"hello {req.params.get('name', 'supportbrain')}")
```

**Why / trap.** Python v2 defines triggers with decorators in code; v1 used a `function.json` per function. `FunctionApp(http_auth_level=...)` sets the default auth level for HTTP triggers, and a single route can override it. `FUNCTION` means the caller must send a function key (for example `?code=`). Run `func start`, then call the route with and without the key to see the difference (README step 2).

---

## Block 2 — Timer trigger: six-field NCRONTAB

**Q.** Add a function that runs every minute, does not run when the host starts, and logs whether a run is late.

```python
import logging
from datetime import datetime, timezone

@app.timer_trigger(schedule="0 */1 * * * *", arg_name="tick", run_on_startup=False)
def sweep(tick: func.TimerRequest) -> None:
    if tick.past_due:
        logging.warning("sweep ran late")
    logging.info("sweep at %s", datetime.now(timezone.utc).isoformat())
```

**Why / trap.** The schedule has six fields, in order: second, minute, hour, day, month, day of week. The default time zone is UTC. `WEBSITE_TIME_ZONE` changes it, but that setting does not apply on Flex Consumption or Consumption Linux. `run_on_startup=True` is for rare cases only. Two more facts: when the app scales out, only one instance runs the timer, and a failed run is **not retried**. It runs again at the next scheduled time. Container Apps jobs use five-field cron instead, so keep the two formats apart.

---

## Block 3 — Service Bus trigger: completion, abandon, and poison messages

**Q.** Add a Service Bus trigger on `jobs` that embeds each article. What happens on success, on an exception, and on the tenth failed delivery?

```python
@app.service_bus_queue_trigger(arg_name="msg", queue_name="jobs", connection="SB_CONN")
def embed_job(msg: func.ServiceBusMessage) -> None:
    body = msg.get_body().decode("utf-8")
    logging.info("embedding %s (delivery %s)", body, msg.delivery_count)
    if "broken" in body:
        raise ValueError("unparseable article")
```

**Why / trap.** By default the runtime **completes** the message when the function succeeds and **abandons** it when the function throws. Poison handling is not configurable in Functions. The queue's `MaxDeliveryCount` dead-letters the message after repeated abandons, so Lab 04's DLQ procedure is how you recover it. `SB_CONN` names an app setting. Locally it lives in `local.settings.json`, and in Azure it is an app setting.

---

## Block 4 — host.json: completion and lock renewal

**Q.** Turn off automatic completion for one app and set the lock-renewal window for long embeddings. Which file holds these settings?

```json
{
  "version": "2.0",
  "extensions": {
    "serviceBus": {
      "autoCompleteMessages": false,
      "maxAutoLockRenewalDuration": "00:05:00"
    }
  }
}
```

**Why / trap.** `host.json` holds runtime behavior and is deployed with the code. `local.settings.json` holds local values and secrets. Turn off `autoCompleteMessages` only when your code settles messages itself. The lock-renewal key is `maxAutoLockRenewalDuration` in extension 5.x and later. The trigger article still shows the older `maxAutoRenewDuration` name for 4.x, and its default is five minutes.

---

## Block 5 — Output binding: enqueue without SDK code

**Q.** Let the HTTP endpoint enqueue an article ID onto a storage queue with a declarative output binding, not an SDK client.

```python
@app.route(route="enqueue", methods=["POST"])
@app.queue_output(arg_name="outq", queue_name="ingest-requests", connection="AzureWebJobsStorage")
def enqueue(req: func.HttpRequest, outq: func.Out[str]) -> func.HttpResponse:
    outq.set(req.get_body().decode("utf-8"))
    return func.HttpResponse("queued", status_code=202)
```

**Why / trap.** A function has exactly one trigger and can have any number of input and output bindings. Triggers start the function; bindings are declarative I/O. `func.Out[str]` is the output parameter type, and `outq.set(...)` writes the message.

---

## Block 6 — local.settings.json and publishing

**Q.** What goes in `local.settings.json`, what does publishing carry, and what must never be published?

```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "<floci-az storage connection string>",
    "SB_CONN": "<Service Bus connection string from Lab 04>"
  }
}
```

**Why / trap.** `local.settings.json` drives **local** runs only. When you publish, add the required settings to the function app's **app settings**, because the local file is not the deployed configuration. Never publish `AzureWebJobsStorage` as `UseDevelopmentStorage=true`. In Azure it must be the real storage account connection. Keep this file out of source control; the template `.gitignore` already excludes it. Recite the deploy command: `func azure functionapp publish <app-name>` (Core Tools).

**Azure-side:** choose the plan by cold-start need. Flex Consumption lets you keep always-ready instances for one latency-sensitive function. Premium keeps pre-warmed instances for the whole app. Consumption has no pre-warm.

---

## Done-when check

- [ ] HTTP, timer, and Service Bus functions run locally with `func start` (Lab 04's `jobs` queue must be up)
- [ ] You can recite the v2 decorators and what `host.json` versus `local.settings.json` control
- [ ] You can name the cold-start trade-off between Consumption, Flex Consumption, and Premium

Cleanup: Ctrl+C the host; `floci az stop` when done.
