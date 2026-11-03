# Remediation Mock 02 — AI-200 (weak-skill sweep, 30 questions, ~45 minutes)

Targets the score report's top-3 priority skills, and nothing else:
- **(a) Develop event- and message-based AI solutions** — Q4, Q5, Q8, Q9, Q11, Q14, Q15, Q19, Q23–Q27 (13)
- **(b) Develop and implement Azure Functions** — Q1–Q3, Q7, Q12, Q17, Q20, Q28 (8)
- **(c) Implement container application hosting** (ACR / App Service, plus the ACR-auth and scale-trap adjacencies) — Q6, Q10, Q13, Q16, Q18, Q21, Q22, Q29, Q30 (9)

Assembled from the retake batch pools (items not used in Mock 02 — every pool item appears at most once across the two mocks). All keys re-verified against live Microsoft Learn pages on 2026-11-04. All scenarios are original.

Rules: closed book. Bar: **≥ 26/30 (87%)**. The Yes/No block (Q24–Q30) is **no-return**: write your answer and don't change it. Note: the block is 7 items here (real exam: 4) to sweep every remaining trap from the weak-skill pools.

---

## Case Study (Q1–Q3) — Fabrikam Claims

Fabrikam Claims is moving an AI claims-intake workload onto Azure Functions. An HTTP trigger on a Flex Consumption plan accepts a scanned claim PDF, validates it, and starts a Durable Functions orchestration. The orchestrator fans out one activity per page to call Azure AI Document Intelligence through an SDK client (not a binding), then fans back in to assemble the full claim text. A second activity calls Azure OpenAI to draft a summary and writes it to Cosmos DB through an output binding. When overall confidence is below 0.75, the orchestration must pause for up to 48 hours waiting for an adjuster's decision before marking the claim reviewed. The Document Intelligence key lives in Key Vault and is referenced from the function app's application settings. Fabrikam wants the HTTP intake function to never show a cold start, without losing the serverless, pay-per-execution model for the rest of the app.

**Q1.** Which hosting configuration best satisfies "no cold start on the HTTP intake function, but keep the rest of the app serverless and pay-per-execution"?
A) Move the whole app to the Premium plan, which keeps one worker perpetually warm
B) Stay on Flex Consumption and configure one or more always-ready instances for the HTTP-triggered function only
C) Switch the whole app to the Dedicated plan with Always On enabled
D) Keep Consumption (legacy) and raise functionTimeout to 10 minutes

**Q2.** (Select TWO) Which two statements about Fabrikam's design are correct?
A) The Document Intelligence and Azure OpenAI calls belong in activity functions, not the orchestrator, because the orchestrator must stay deterministic
B) The orchestrator can call Azure OpenAI directly because reading a model response doesn't change orchestrator state
C) The 48-hour adjuster wait should use time.sleep() inside the orchestrator so the workflow pauses precisely
D) The 48-hour adjuster wait should use context.create_timer raced against context.wait_for_external_event, not time.sleep()
E) Because the HTTP intake function and the orchestrator are in the same Function App, they must share one trigger

**Q3.** (Dropdown) Select the correct values: the orchestrator schedules the page-level Document Intelligence activities and waits for the whole group with `results = yield context.____(tasks)`; for the adjuster wait it races `context.wait_for_external_event(...)` against a durable timer using `winner = yield context.____([...])`.
- Blank 1 options: `task_all` / `task_any`
- Blank 2 options: `task_all` / `task_any`

---

## Section 2 — Regular questions (Q4–Q23)

**Q4.** (Select TWO) A custom Event Grid topic carries two event types from one pipeline: `com.contoso.ai.ContentClassified` (with a `data.status` of `flagged` or `approved`) and `com.contoso.ai.ImageDecodeFailed`. Which TWO subscription configurations correctly route ONLY flagged classifications to a review-queue subscription, with no extra filtering code in the review-queue service itself?
A) An advanced filter: `data.status StringIn flagged`
B) A `--subject-begins-with` filter added to the dashboard subscription
C) An event-type filter: `--included-event-types com.contoso.ai.ContentClassified`
D) Read every event in the handler and discard non-flagged ones in code
E) An advanced filter: `data.status StringNotIn flagged`
F) A `--subject-ends-with .jpg` filter

**Q5.** (Ordering) Arrange the steps to safely reprocess a batch of dead-lettered messages after fixing the root-cause bug.
A) Call `complete_message()` on the original dead-lettered copy to remove it from the DLQ
B) Inspect `dead_letter_reason` and `dead_letter_error_description` to confirm the root cause is fixed
C) Open a receiver scoped to the DLQ sub-queue (`sub_queue=ServiceBusSubQueue.DEAD_LETTER`) and receive the poisoned messages
D) Build a new `ServiceBusMessage` with the same body and properties and `send_messages()` it to the original queue

**Q6.** How should an App Service web app authenticate to pull its container image from ACR without storing a password anywhere?
A) Enable the ACR admin user and store its username/password as app settings
B) Assign the web app a managed identity, grant it the `AcrPull` role on the registry, and set `acrUseManagedIdentityCreds` to `true`
C) Use a Docker Hub service account instead of ACR
D) Store a personal access token in `local.settings.json`

**Q7.** (Ordering) Arrange the steps to switch a Service Bus-triggered function from a connection-string app setting to an identity-based connection.
A) Set the app setting `ServiceBusConnection__fullyQualifiedNamespace` to `<namespace>.servicebus.windows.net`
B) Enable a system-assigned managed identity on the function app
C) Remove the old `ServiceBusConnection` connection-string app setting
D) Assign the `Azure Service Bus Data Receiver` role to the function app's identity on the namespace

**Q8.** A team builds a plain HTTP-trigger Azure Function (NOT the dedicated Event Grid trigger binding) as a generic webhook for Event Grid. What must they add themselves?
A) Nothing — Azure Functions always auto-validates every Event Grid subscription
B) Code that echoes back the `validationCode` (or supports the manual `validationUrl` GET) — this endpoint type isn't auto-validated
C) A Service Bus queue placed in front of the function
D) An Event Grid domain wrapping the function

**Q9.** (Ordering) Arrange the sequence of events for a message that a PeekLock consumer can never successfully settle, until `MaxDeliveryCount` is reached.
A) The broker moves the message to the DLQ with reason `MaxDeliveryCountExceeded`
B) A consumer receives the message under PeekLock and crashes before settling
C) The lock duration elapses and the message becomes available again, with `DeliveryCount` incremented
D) Steps B and C repeat until the delivery count exceeds the configured maximum

**Q10.** (Dropdown) An AKS deployment named `catalog-api` must pull its image from a private ACR with no registry credentials stored anywhere in the cluster. Select the correct values: identity mechanism = **____**; role granted to it = **____**.
- Mechanism options: `managed identity` / `imagePullSecret` / `service principal password`
- Role options: `AcrPull` / `Contributor` / `Reader`

**Q11.** (Ordering) Arrange the steps to start receiving events from a Partner Events partner (e.g., Stripe) in your Azure subscription:
A) Subscribe to events by creating an event subscription on the partner topic
B) Request the partner forward events; the partner provisions a partner topic in your resource group
C) Authorize the partner to create a partner topic in a resource group you designate
D) Activate the partner topic

**Q12.** (Ordering) Arrange the Durable Functions async-HTTP-API ("polling consumer") flow in the order it actually happens.
A) The client polls the `statusQueryGetUri` URL
B) The HTTP-triggered client function starts the orchestration and returns HTTP 202 with a `Location` header
C) When the orchestration finishes, the polled endpoint returns HTTP 200 with the result
D) The caller sends an HTTP request that starts a long-running orchestration

**Q13.** (Dropdown) In the App Service sidecar model, select the correct values: the main container must listen on port **____**, and the two containers communicate over **____**.
- Port blank options: `80 or 8080` / `any port the app chooses` / `443 only`
- Communication blank options: `localhost` / `the sidecar's container name` / `a private DNS zone`

**Q14.** (Matching) Match each Service Bus concept to its correct description. Options may be used once, more than once, or not at all.

Concepts: 1) Correlation filter 2) `defer_message()` 3) Auto-forwarding 4) `AutoLockRenewer`

Descriptions:
A) Chains a queue/subscription to another queue/topic; more than 4 hops dead-letters the message
B) Keeps a message in the queue but removes it from normal delivery; retrieve later by sequence number
C) Exact-matches specific properties like `SessionId` or `MessageId`; more efficient than a SQL expression
D) Automatically renews a PeekLock in the background until a specified duration elapses
E) Permanently deletes a message the instant it's delivered

**Q15.** (Matching) Match each requirement to the Azure messaging service that best satisfies it. Options may be used once, more than once, or not at all.
1. Needs duplicate detection and transactions for financial order processing
2. Millions of IoT telemetry events per second through a Kafka-compatible endpoint
3. A Blob Created event pushed to a webhook, with a built-in dead-letter option
4. Automatically captures the raw event stream to Blob Storage for later replay
5. Reacts to a Key Vault `SecretNearExpiry` system-topic event

Options: A) Event Grid B) Event Hubs C) Service Bus

**Q16.** Which ACR role grants permission to delete artifacts and tags across the registry, but does NOT grant permission to delete the registry resource itself?
A) `AcrPull`
B) `AcrPush`
C) `AcrDelete`
D) Owner

**Q17.** (Matching) Match each Functions hosting plan to the fact that best describes it. Options may be used once, more than once, or not at all.
1. Flex Consumption  2. Premium  3. Dedicated (App Service)  4. Container Apps hosting
A) Best when functions need GPU access or must run alongside other containerized microservices
B) Recommended default for new serverless function apps; configurable per-function always-ready instances
C) functionTimeout default of 5 minutes and a hard maximum of 10 minutes
D) Pre-warmed instances keep the plan "perpetually warm," fully eliminating cold start
E) Best for long-running scenarios where Durable Functions can't be used, when there's already underutilized App Service capacity

**Q18.** (Ordering) Arrange the steps for safely rolling out a new image tag to a container that must never silently pick up an unvetted build.
A) Push the image to ACR under a unique, traceable tag (e.g. including the Git commit SHA)
B) Point the App Service container setting at the new explicit tag and verify the app starts cleanly
C) Lock the now-live production tag with `--write-enabled false` so it can't be deleted or overwritten
D) Build and test the image (e.g. with a multi-step ACR task) before anything is pushed

**Q19.** (Code fill-in) Complete the Python code to receive from a Service Bus queue's dead-letter sub-queue and print why each message landed there:

```python
with client.get_queue_receiver(
    queue_name="claims-intake",
    sub_queue=_____________________,
    max_wait_time=10
) as dlq_receiver:
    for msg in dlq_receiver:
        print(msg._____________________, msg._____________________)
```

Fill in the three blanks.

**Q20.** (Fill-in) Write the Python v2 decorator line that applies an exponential-backoff retry policy of up to 5 attempts, starting at 2 seconds and capping at 30 seconds, to a Kafka-triggered function.
Your answer: ______________________________________________

**Q21.** (CLI fill-in) Write the Azure CLI command that runs the EXISTING image `api:v1` already in registry `fabrikamreg` (no new build) to execute the smoke-test command `pytest`, using no source context.

**Q22.** (CLI fill-in) Write the single `az` CLI command that lets an AKS cluster's node pool pull images from an ACR named `contosoacr` in resource group `rg1` — **without** creating any Kubernetes `imagePullSecret`. Use cluster name `contoso-aks`.

**Q23.** (Dropdown) A flagged event must never be silently lost while its webhook endpoint is offline for a few minutes during deploys. To guarantee this, configure dead-lettering on the subscription: dead-lettering is **____** by default, and enabling it requires specifying an existing **____** as the `--deadletter-endpoint`.
- Blank 1 options: `disabled` / `enabled`
- Blank 2 options: `Blob Storage container` / `Service Bus queue` / `Event Hubs namespace`

---

## Section 3 — Yes/No, no-return (Q24–Q30)

**Q24.** A message that is explicitly deferred with `defer_message()` and later passes its TTL is automatically moved to the dead-letter queue. Yes / No

**Q25.** Losing a PeekLock because of a Service Bus service-side update (not because your code ran too long) increments the message's `DeliveryCount`. Yes / No

**Q26.** Pull delivery is available on classic (non-namespace) Event Grid custom topics. Yes / No

**Q27.** An Azure Function configured with the Event Grid trigger binding must implement the `SubscriptionValidationEvent` handshake itself in its own code. Yes / No

**Q28.** An orchestrator function may call `time.sleep(5)` directly as long as the delay is short and the app is on the Premium plan. Yes / No

**Q29.** Azure App Service sidecar containers are available for both Linux and Windows custom containers today. Yes / No

**Q30.** A Container App with only an HTTP or CPU scaling rule will still scale out correctly when a Service Bus queue it also happens to read from fills up, because Container Apps automatically correlates all event sources for an app. Yes / No

---

## Answer key

| Q | Ans | Domain | Why |
|---|---|---|---|
| 1 | B | integration | Flex Consumption warms only the latency-sensitive function (per-function always-ready); Premium warms the whole plan |
| 2 | A, D | integration | orchestrator must stay deterministic (no model calls); durable timer/external-event race replaces time.sleep() |
| 3 | task_all / task_any | integration | task_all = fan-in wait-for-all; task_any = race event vs timer |
| 4 | A, C | integration | event-type filter isolates ContentClassified from ImageDecodeFailed; advanced filter isolates flagged from approved; D is the filter-in-handler trap |
| 5 | C -> B -> D -> A | integration | receive from DLQ, diagnose via reason/description, send a fresh copy to the original queue, complete the DLQ copy |
| 6 | B | containers | managed identity + AcrPull + acrUseManagedIdentityCreds avoids storing any registry password |
| 7 | B -> D -> A -> C | integration | identity first, then role, then the __fullyQualifiedNamespace setting, then remove the old secret last |
| 8 | B | integration | only Logic Apps, Automation webhooks, and the Event Grid trigger binding auto-handle validation; a plain HTTP function isn't on that list |
| 9 | B -> C -> D -> A | integration | crash, lock expiry increments DeliveryCount, repeat, then MaxDeliveryCountExceeded dead-letters it |
| 10 | managed identity / AcrPull | containers | no stored registry credentials; same pattern as AKS kubelet identity |
| 11 | C -> B -> D -> A | integration | authorize → partner provisions → activate → subscribe |
| 12 | D -> B -> A -> C | integration | request starts it → 202 + Location → client polls → 200 on completion |
| 13 | `80 or 8080` / `localhost` | containers | sidecar model fixes the main container to 80/8080; all containers share one network namespace |
| 14 | 1-C, 2-B, 3-A, 4-D | integration | E describes ReceiveAndDelete — unused distractor |
| 15 | 1-C, 2-B, 3-A, 4-B, 5-A | integration | transactions/dup-detection = Service Bus; Kafka-scale streaming + Capture = Event Hubs; push+DLQ and system topics = Event Grid |
| 16 | C | containers | AcrDelete removes artifacts/tags only; registry deletion needs a control-plane role |
| 17 | 1-B, 2-D, 3-E, 4-A | integration | C (Consumption legacy timeouts) is an unused distractor |
| 18 | D -> A -> B -> C | containers | build/test, push under unique tag, cut over + verify, then lock the live tag (`az acr repository update --write-enabled false`) |
| 19 | `ServiceBusSubQueue.DEAD_LETTER`, then `dead_letter_reason`, `dead_letter_error_description` | integration | the SDK's sub_queue parameter avoids hand-building the $deadletterqueue path |
| 20 | `@app.retry(strategy="exponential_backoff", max_retry_count=5, minimum_interval="00:00:02", maximum_interval="00:00:30")` | integration | exponential_backoff takes minimum_interval + maximum_interval; delay_interval belongs to fixed_delay |
| 21 | `az acr run --registry fabrikamreg --cmd "api:v1 pytest" /dev/null` | containers | `az acr run` executes an image already in the registry; /dev/null = no source context |
| 22 | `az aks update -n contoso-aks -g rg1 --attach-acr contosoacr` | containers | grants AcrPull to the AKS kubelet identity; no imagePullSecret needed (not supported for ABAC-enabled registries) |
| 23 | disabled / Blob Storage container | integration | dead-lettering is off by default; the storage container must already exist — Event Grid never creates it |
| 24 | No | integration | deferred messages are exempt from TTL-expiry dead-lettering until retrieved by sequence number |
| 25 | No | integration | service-side lock loss raises MessageLockLostException WITHOUT incrementing DeliveryCount; only lock expiry does |
| 26 | No | integration | pull delivery exists only for topics in an Event Grid namespace; classic topics/domains are push-only |
| 27 | No | integration | the Event Grid trigger extension performs the validation handshake automatically |
| 28 | No | integration | orchestrators must never block/sleep directly, on any plan — use context.create_timer() |
| 29 | No | containers | the sidecar model is documented for Linux App Service apps only |
| 30 | No | containers | HTTP/CPU rules have zero visibility into Service Bus — only a custom azure-servicebus KEDA rule reads queue depth |

## Scorecard

| Weak skill | Questions | Your score | Target |
|---|---|---|---|
| (a) Event- and message-based | Q4, Q5, Q8, Q9, Q11, Q14, Q15, Q19, Q23, Q24, Q25, Q26, Q27 (13) | __ / 13 | ≥ 11 |
| (b) Azure Functions | Q1, Q2, Q3, Q7, Q12, Q17, Q20, Q28 (8) | __ / 8 | ≥ 7 |
| (c) Container application hosting | Q6, Q10, Q13, Q16, Q18, Q21, Q22, Q29, Q30 (9) | __ / 9 | ≥ 8 |
| **Total** | | **__ / 30** | **≥ 26 (87%)** |

## Weak-skill map (drill every miss the same day)

All Anki searches are within `deck:AI-200`; add `tag:retake1` to scope to the new cards. For every miss: open the cited URL, re-read the exact fact, then re-drill the tagged cards before moving on.

| Q | Study-guide skill | Anki drill | Learn URL | From |
|---|---|---|---|---|
| 1 | Sec 3 · Functions — hosting plans | `tag:functions tag:hosting` | https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan | functions Q1 |
| 2 | Sec 3 · Functions — Durable orchestration rules | `tag:functions tag:durable` | https://learn.microsoft.com/en-us/training/modules/orchestrate-durable-functions/2-separate-orchestrator-activity-responsibilities/ | functions Q2 |
| 3 | Sec 3 · Functions — fan-out/fan-in | `tag:functions tag:durable` | https://learn.microsoft.com/en-us/training/modules/orchestrate-durable-functions/3-apply-fan-out-fan-in/ | functions Q3 |
| 4 | Sec 3 · Event Grid — filters | `tag:eventgrid tag:filters` | https://learn.microsoft.com/en-us/azure/event-grid/event-filtering | eventgrid Q2 |
| 5 | Sec 3 · Service Bus — DLQ handling | `tag:servicebus tag:dlq` | https://learn.microsoft.com/en-us/training/modules/queue-process-operations-service-bus/5-process-messages-reliably/ | servicebus Q7 |
| 6 | Sec 1 · App Service — pull from ACR | `tag:acr tag:appservice` | https://learn.microsoft.com/en-us/azure/app-service/tutorial-custom-container | acr-appservice Q1 |
| 7 | Sec 3 · Functions — identity-based connections | `tag:functions tag:identity` | https://learn.microsoft.com/en-us/training/modules/build-backends-azure-functions/6-configure-identity-access/ | functions Q7 |
| 8 | Sec 3 · Event Grid — endpoint validation | `tag:eventgrid tag:validation` | https://learn.microsoft.com/en-us/azure/event-grid/end-point-validation-event-grid-events-schema | eventgrid Q5 |
| 9 | Sec 3 · Service Bus — DLQ handling | `tag:servicebus tag:dlq` | https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-dead-letter-queues | servicebus Q8 |
| 10 | Sec 1 · ACR — pull auth (AKS) | `tag:acr tag:aks` | https://learn.microsoft.com/en-us/azure/aks/cluster-container-registry-integration | aca-aks Q3 |
| 11 | Sec 3 · Event Grid — partner events | `tag:eventgrid` | https://learn.microsoft.com/en-us/azure/event-grid/partner-events-overview | eventgrid Q7 |
| 12 | Sec 3 · Functions — Durable HTTP API | `tag:functions tag:durable` | https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-http-features | functions Q8 |
| 13 | Sec 1 · App Service — sidecars | `tag:appservice tag:sidecar` | https://learn.microsoft.com/en-us/azure/app-service/overview-sidecar | acr-appservice Q3 |
| 14 | Sec 3 · Service Bus — filters/deferral | `tag:servicebus tag:filters` | https://learn.microsoft.com/en-us/azure/service-bus-messaging/topic-filters | servicebus Q9 |
| 15 | Sec 3 · Messaging service selection | `tag:eventgrid tag:eventhubs` | https://learn.microsoft.com/en-us/azure/service-bus-messaging/compare-messaging-services | eventgrid Q9 |
| 16 | Sec 1 · ACR — roles | `tag:acr tag:roles` | https://learn.microsoft.com/en-us/azure/container-registry/container-registry-rbac-built-in-roles-overview | acr-appservice Q6 |
| 17 | Sec 3 · Functions — hosting plans | `tag:functions tag:hosting` | https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale | functions Q9 |
| 18 | Sec 1 · ACR — tagging/locking | `tag:acr tag:acrtasks` | https://learn.microsoft.com/en-us/training/modules/store-manage-containers-azure-container-registry/4-tag-version-images/ | acr-appservice Q8 |
| 19 | Sec 3 · Service Bus — DLQ SDK | `tag:servicebus tag:sdk` | https://learn.microsoft.com/en-us/training/modules/queue-process-operations-service-bus/5-process-messages-reliably/ | servicebus Q10 |
| 20 | Sec 3 · Functions — retry policies | `tag:functions tag:retry` | https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-error-pages | functions Q10 |
| 21 | Sec 1 · ACR Tasks | `tag:acr tag:acrtasks` | https://learn.microsoft.com/en-us/training/modules/store-manage-containers-azure-container-registry/3-build-run-acr-tasks/ | acr-appservice Q10 |
| 22 | Sec 1 · AKS–ACR integration | `tag:aks tag:acr` | https://learn.microsoft.com/en-us/azure/aks/cluster-container-registry-integration | aca-aks Q10 |
| 23 | Sec 3 · Event Grid — dead-lettering | `tag:eventgrid tag:dlq` | https://learn.microsoft.com/en-us/azure/event-grid/delivery-and-retry | eventgrid Q3 |
| 24 | Sec 3 · Service Bus — expiration/deferral | `tag:servicebus tag:dlq` | https://learn.microsoft.com/en-us/azure/service-bus-messaging/message-deferral | servicebus Q11 |
| 25 | Sec 3 · Service Bus — locks | `tag:servicebus tag:dlq` | https://learn.microsoft.com/en-us/azure/service-bus-messaging/message-transfers-locks-settlement | servicebus Q12 |
| 26 | Sec 3 · Event Grid — pull delivery | `tag:eventgrid tag:namespaces` | https://learn.microsoft.com/en-us/azure/event-grid/overview | eventgrid Q11 |
| 27 | Sec 3 · Event Grid — validation handshake | `tag:eventgrid tag:validation` | https://learn.microsoft.com/en-us/azure/event-grid/end-point-validation-event-grid-events-schema | eventgrid Q12 |
| 28 | Sec 3 · Functions — orchestrator constraints | `tag:functions tag:durable` | https://learn.microsoft.com/en-us/training/modules/orchestrate-durable-functions/2-separate-orchestrator-activity-responsibilities/ | functions Q12 |
| 29 | Sec 1 · App Service — sidecars | `tag:appservice tag:sidecar` | https://learn.microsoft.com/en-us/azure/app-service/overview-sidecar | acr-appservice Q12 |
| 30 | Sec 1 · Container Apps — scale rules | `tag:aca tag:keda` | https://learn.microsoft.com/en-us/azure/container-apps/scale-app | aca-aks Q11 |
