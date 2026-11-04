# Solution 07 — OpenTelemetry + KQL (answer key)

> **Attempt-first rule.** First pass: you may consult this key. The two runs that count toward *Solid Practice* must be done with this file **closed**. When you're ready for a counted run, close it and work from [README.md](README.md) alone.

**The Case Thread.** SupportBrain's upload path crosses two services: the intake API and the OCR worker. Both must appear in **one** Jaeger trace, and KQL must answer "which tenant is slow". Every block below is the next thing you do on that job.

**Setup (do once, SETUP.md §3):**

```bash
docker start jaeger 2>/dev/null || docker run -d --name jaeger -p 16686:16686 -p 4318:4318 jaegertracing/all-in-one:latest
docker start kustainer 2>/dev/null || docker run -d --name kustainer -e ACCEPT_EULA=Y -p 8080:8080 mcr.microsoft.com/azuredataexplorer/kustainer-linux:latest
source ../../.venv/bin/activate          # from this folder
```

Part A's blocks paste into `telemetry.py`. Part B runs in a Kusto client, not Python.

> **Verification status (2026-11-04).** The span logic in Part A (context propagation, span kinds, statuses, sampler) was run in-process with an in-memory exporter and passed. Jaeger and kustainer were **not** running, so the OTLP export lines and every KQL line are unexecuted.

---

## Part A — OpenTelemetry → Jaeger

### Block 1 — Minimal tracer

**Q.** Send spans from the intake API to Jaeger over OTLP/HTTP. Which port and path does the exporter use, and why does `service.name` matter?

```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

provider = TracerProvider(resource=Resource.create({"service.name": "supportbrain-api"}))
provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces")))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("supportbrain")

with tracer.start_as_current_span("checkout"):
    pass
provider.force_flush()
```

**Why / trap.** OTLP over HTTP listens on **4318** at `/v1/traces`. The Jaeger UI is on 16686. `service.name` is the label Jaeger shows for each service. `SimpleSpanProcessor` exports synchronously, which suits a lab; production uses `BatchSpanProcessor`.

### Block 2 — Attributes, events, and status

**Q.** Tag a span with the tenant, record a cache miss, and mark a failed OCR call as an error.

```python
from opentelemetry.trace import Status, StatusCode

with tracer.start_as_current_span("ingest-bol") as span:
    span.set_attribute("tenant", "contoso")
    span.add_event("cache-miss")
    try:
        raise TimeoutError("ocr vendor timed out")
    except TimeoutError as exc:
        span.record_exception(exc)                                  # adds an "exception" event
        span.set_status(Status(StatusCode.ERROR, "ocr vendor timeout"))
```

**Why / trap.** `record_exception` attaches the exception as an event; `set_status(ERROR)` marks the span failed. Both are needed: an event without a status still looks successful in the trace list.

### Block 3 — One trace across two services

**Q.** The API publishes a BOL message to `jobs`, and the OCR worker processes it. Carry `traceparent` through the Service Bus message so both spans share one trace ID.

```python
import os
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from opentelemetry import propagate
from opentelemetry.trace import SpanKind

client = ServiceBusClient.from_connection_string(os.environ["SB_CONN"])

# producer (intake API)
with tracer.start_as_current_span("upload-bol", kind=SpanKind.PRODUCER):
    carrier: dict[str, str] = {}
    propagate.inject(carrier)                                       # writes "traceparent" into the dict
    with client.get_queue_sender("jobs") as sender:
        sender.send_messages(ServiceBusMessage(b"bol-1042", application_properties=carrier))

# consumer (OCR worker)
with client.get_queue_receiver("jobs", max_wait_time=5) as receiver:
    for msg in receiver.receive_messages(max_message_count=1, max_wait_time=5):
        ctx = propagate.extract(dict(msg.application_properties))
        with tracer.start_as_current_span("ocr-job", context=ctx, kind=SpanKind.CONSUMER):
            receiver.complete_message(msg)
```

**Why / trap.** Service Bus carries your data as application properties, and it does **not** add trace context on its own. The app must inject on send and extract on receive. The header has the form `00-<32-hex trace id>-<16-hex parent span id>-<flags>`. In-process, the consumer span shared the producer's trace ID and pointed at the producer span as its parent. To see **two** services in Jaeger, run the producer and the consumer as two scripts with different `service.name` values.

Exam paragraph (done-when): *The producer injects the W3C `traceparent` into the message's application properties. The consumer extracts it and starts its span as a child of the producer's span, so both share one trace ID. Service Bus does not do this for you; the application must.*

### Block 4 — Span kinds and sampling

**Q.** Which span kind fits each operation? Keep about 10 percent of traces but follow the upstream decision so a trace is not half-sampled across services.

```python
from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased

sampler = ParentBased(root=TraceIdRatioBased(0.1))              # ~10% of new traces; children follow the parent
print(sampler.get_description())
```

**Why / trap.** Span kinds: `SERVER` for inbound HTTP, `CLIENT` for outbound calls, `PRODUCER` for sends, `CONSUMER` for receives, and `INTERNAL` for everything else. `ParentBased` honors the parent's decision, and the ratio applies only to new root traces. The environment-variable form is `OTEL_TRACES_SAMPLER=parentbased_traceidratio` with `OTEL_TRACES_SAMPLER_ARG=0.1` (OpenTelemetry sampler configuration; not re-fetched here).

### Block 5 — Azure-side: Application Insights

**Q.** Where do the same spans land in Azure? Say it out loud.

**A.** The Azure Monitor OpenTelemetry distribution (`configure_azure_monitor`) sends spans to Application Insights. Server and consumer spans become `requests` rows; client, producer, and internal spans become `dependencies` rows (Azure-side mapping, not re-fetched here). The package is not in `requirements.txt`, so this stays theory in the lab.

---

## Part B — KQL on the Kusto emulator

Connect Kusto.Explorer or Kusto.CLI to the emulator's HTTP query endpoint at `http://localhost:8080`. The emulator supports management and ingestion commands but **not** managed ingestion (Event Hubs, Event Grid, streaming), and its data lives in the container.

### Block 6 — Create and fill the table

**Q.** Create `requests` with the App Insights-style columns, then ingest rows with an inline command. Repeat the sample rows until you have about 50.

```kusto
.create table requests (timestamp:datetime, name:string, duration:real, resultCode:string, user_Id:string)

.ingest inline into table requests <|
2026-11-04T09:00:00Z,/search,120.5,200,ada
2026-11-04T09:01:00Z,/search,980.2,500,grace
2026-11-04T09:02:00Z,/upload,2100.0,200,ada
```

**Why / trap.** `.ingest inline` is an ingestion command, which the emulator supports. Managed ingestion pipelines are not available locally, so this inline path replaces them.

### Block 7 — The five queries

**Q.** Write, from memory, the errors of the last hour, the volume per five minutes as a chart, the p95 duration per endpoint, the top users, and a join to a users table.

```kusto
// errors in the last hour
requests
| where timestamp > ago(1h)
| where resultCode != "200"

// volume per 5 minutes, drawn as a time chart
requests
| summarize hits = count() by bin(timestamp, 5m)
| render timechart

// p95 duration per endpoint, slowest first
requests
| summarize p95 = percentile(duration, 95) by name
| order by p95 desc

// top 10 users by request count
requests
| summarize hits = count() by user_Id
| top 10 by hits

// join practice
let users = datatable(user_Id:string, tier:string)["ada", "enterprise", "grace", "standard"];
requests
| join kind=inner (users) on user_Id
```

**Why / trap.** Put `where` before `summarize` so the aggregation sees less data. `ago()` anchors the window. `bin(timestamp, 5m)` buckets rows for `render timechart`. `percentile(duration, 95)` gives the 95th percentile. `top 10 by hits` sorts and limits in one step. Aliases (`p95 =`, `hits =`) keep the column names predictable.

### Block 8 — Operator pairs to drill

**Q.** Which operator fits which job: `has` or `contains`; `project` or `extend`; `let`?

**A.** `has` matches a whole term and is the fast choice on indexed text; `contains` matches any substring and is slower. `project` keeps only the columns you name; `extend` adds a column and keeps the rest. `let` binds a name to a value or a table, which makes long queries readable.

---

## Done-when check

- [ ] Part A's trace shows two services in one Jaeger trace (run the producer and consumer as two services)
- [ ] You can write all five KQL queries cold, twice
- [ ] You can explain `traceparent` propagation in one paragraph (see Block 3)

Cleanup: `docker rm -f jaeger kustainer` (keep kustainer if you're mid-cram; it's about 2 GB).
