# Lab 07 — OpenTelemetry + KQL

**Study-guide bullets covered:** trace distributed systems with OpenTelemetry SDKs · write KQL to analyze logs and metrics.

**Setup:** Jaeger (`jaegertracing/all-in-one`, UI :16686, OTLP HTTP :4318) and the Kusto emulator (`kustainer`, :8080) from [SETUP.md](../../SETUP.md).

## Part A — OpenTelemetry → Jaeger

1. **Minimal tracer.** `TracerProvider` + `SimpleSpanProcessor(OTLPSpanExporter("http://localhost:4318/v1/traces"))`; wrap a function in `with tracer.start_as_current_span("checkout"):`. Find it in the Jaeger UI.
2. **Attributes, events, status.** Add `span.set_attribute("tenant", t)`, `span.add_event("cache-miss")`, and force an exception to see `status=ERROR`.
3. **Distributed trace.** Two scripts (or a Function from Lab 05 + a Service Bus receiver): inject context into a Service Bus message's application properties (`traceparent`), extract it in the consumer (`propagate.extract`), start a child span. One trace across processes in Jaeger.
4. **Exam knowledge.** Span kinds (server/client/internal/producer/consumer), sampling (`parentbased_always_on` vs `traceidratio`), and the Azure landing zone: Azure Monitor OpenTelemetry distro → Application Insights.

## Part B — KQL on the Kusto emulator

1. Create a table `requests` (timestamp datetime, name string, duration double, resultCode string, user_Id string), ingest ~50 rows (`requests` App Insights schema, fake data).
2. Write, from memory:
   - errors last hour: `requests | where timestamp > ago(1h) | where resultCode != "200"`
   - per-5-min volume: `requests | summarize count() by bin(timestamp, 5m) | render timechart`
   - p95 by endpoint: `requests | summarize percentile(duration, 95) by name | order by percentile_duration_ desc`
   - top users: `requests | summarize count() by user_Id | top 10 by count_`
   - join practice: make a `users` table and `join kind=inner on user_Id`
3. Drill `has` vs `contains`, `project` vs `extend`, `let`.

## Done when

- [ ] Part A trace shows 2+ services in one Jaeger trace
- [ ] You can write all five KQL queries cold, twice
- [ ] You can explain traceparent propagation in one paragraph

## Cleanup

`docker rm -f jaeger kustainer` (keep kustainer if you're mid-cram; it's ~2 GB).
