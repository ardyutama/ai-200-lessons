# Lab 04 — Azure Service Bus (floci-az, AMQP :5673)

**Study-guide bullets covered:** queue and process back-end operations · dead-letter handling · topics and subscriptions.

**Setup:** `floci az start && eval $(floci az env)`; Python `azure-servicebus`. floci-az exposes Service Bus AMQP on `amqp://localhost:5673` — use the connection string `floci az env` exports.

## Steps

1. **Queue round-trip.** Create queue `jobs`; send 5 `ServiceBusMessage`s with application properties (`priority`, `tenant`); receive with PeekLock and `complete_message()` each.
2. **Settlement semantics.** Re-send one message and `abandon_message()` it — observe redelivery and the delivery count increment. Then `dead_letter_message(msg, reason="poison")` — read it back from the DLQ (`<queue>/$deadletterqueue` / `sub_queue` option in the SDK).
3. **MaxDeliveryCount.** Conceptual + config: set the queue's max delivery count to 2, abandon twice, watch the message dead-letter itself.
4. **Topics/subscriptions.** Create topic `events` with two subscriptions: `high` (SQL filter `priority = 'high'`) and `all` (default TrueFilter). Publish 3 messages with mixed priorities; verify routing. Swap the SQL filter for a correlation filter and explain the efficiency difference.
5. **Modes.** Contrast PeekLock vs ReceiveAndDelete — which is at-most-once, and when that's acceptable.
6. **Extras to name-drop:** sessions (`session_id` ordering), scheduled messages, duplicate detection (`message_id` window), auto-forwarding.

## Done when

- [ ] Steps 1–4 scripted from memory, twice
- [ ] You can list all four DLQ triggers unprompted
- [ ] You can argue Service Bus vs Event Grid in two sentences (pull vs push; commands vs facts)

## Cleanup

`floci az stop`
