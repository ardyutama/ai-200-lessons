# Solution 04 — Azure Service Bus (answer key)

> **Attempt-first rule.** First pass: you may consult this key. The two runs that count toward *Solid Practice* must be done with this file **closed**. When you're ready for a counted run, close it and work from [README.md](README.md) alone.

**The Case Thread.** SupportBrain (from [Lab 02](../02-postgres-pgvector/SOLUTION.md)) ingests articles through a queue. Each article becomes a `jobs` message tagged with `tenant` and `priority`. One malformed article must never block the queue, and every failed job must stay visible for a human. Every block below is the next thing you do on that job.

**Setup (do once):**

```bash
floci az start && eval $(floci az env)     # README setup line: Service Bus AMQP on localhost:5673
export SB_CONN="<the Service Bus connection string that floci az env exports>"
source ../../.venv/bin/activate            # from this folder
```

Blocks paste into `servicebus.py` top to bottom. Block 1 defines `client` and `admin`; later blocks reuse them.

> **Note on the runtime split.** floci-az runs Service Bus locally, so every block targets it. Anything marked **Azure-side** is say-it-out-loud exam knowledge.

> **Verification status (2026-11-04).** Method names, parameters, and enum values were checked against the installed `azure-servicebus` package. Docker was stopped when this was written, so these blocks have **not** been run against floci-az yet. Run Block 1 first.

---

## Block 1 — Queue round-trip

**Q.** Create queue `jobs`, send five article jobs with `priority` and `tenant` application properties, then receive and settle each one. Which receive mode is the default, and what does settlement do?

```python
import os
from azure.core.exceptions import ResourceExistsError
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.servicebus.management import ServiceBusAdministrationClient

CONN = os.environ["SB_CONN"]
admin = ServiceBusAdministrationClient.from_connection_string(CONN)
client = ServiceBusClient.from_connection_string(CONN)

try:
    admin.create_queue("jobs")
except ResourceExistsError:
    pass

with client.get_queue_sender("jobs") as sender:
    sender.send_messages([
        ServiceBusMessage(
            f"article-{i}",
            application_properties={"priority": "high" if i % 2 == 0 else "low", "tenant": "contoso"},
        )
        for i in range(5)
    ])

with client.get_queue_receiver("jobs", max_wait_time=5) as receiver:    # PEEK_LOCK is the default
    for msg in receiver.receive_messages(max_message_count=5, max_wait_time=5):
        print(b"".join(msg.body).decode(), msg.application_properties)
        receiver.complete_message(msg)                                    # removes the message
```

**Why / trap.** The default receive mode is **PeekLock**: the broker locks the message until you settle it. `complete_message` removes it; `abandon_message` puts it back. A crash before settlement means redelivery, so PeekLock is **at-least-once**. Exam line: *PeekLock is at-least-once, so the handler must be idempotent.*

---

## Block 2 — Settlement: abandon, then dead-letter

**Q.** Send one malformed article. Abandon it once and watch `DeliveryCount` rise. Then dead-letter it with a reason and read it back from the dead-letter sub-queue.

```python
from azure.servicebus import ServiceBusSubQueue

with client.get_queue_sender("jobs") as sender:
    sender.send_messages(ServiceBusMessage("article-broken", application_properties={"tenant": "fabrikam", "priority": "high"}))

with client.get_queue_receiver("jobs", max_wait_time=5) as receiver:
    msg = receiver.receive_messages(max_message_count=1, max_wait_time=5)[0]
    print("first delivery:", msg.delivery_count)
    receiver.abandon_message(msg)                                  # back on the queue, count goes up

    msg = receiver.receive_messages(max_message_count=1, max_wait_time=5)[0]
    print("second delivery:", msg.delivery_count)
    receiver.dead_letter_message(msg, reason="poison", error_description="unparseable article")

with client.get_queue_receiver("jobs", sub_queue=ServiceBusSubQueue.DEAD_LETTER, max_wait_time=5) as dlq:
    for dead in dlq.receive_messages(max_message_count=10, max_wait_time=5):
        print(dead.dead_letter_reason, "|", dead.dead_letter_error_description)
        dlq.complete_message(dead)
```

**Why / trap.** The dead-letter queue is a **sub-queue** of `jobs`, not a separate queue. `sub_queue=ServiceBusSubQueue.DEAD_LETTER` reads it. Abandon increments `DeliveryCount`. An explicit dead-letter ends the cycle at once and stores your reason and description.

---

## Block 3 — MaxDeliveryCount: the broker dead-letters for you

**Q.** Set the maximum delivery count to 2, abandon twice, and show that the broker dead-letters the message on the next attempt. Use a second queue so `jobs` keeps its default.

```python
try:
    admin.create_queue("jobs-max2", max_delivery_count=2)
except ResourceExistsError:
    pass

with client.get_queue_sender("jobs-max2") as sender:
    sender.send_messages(ServiceBusMessage("article-flaky"))

with client.get_queue_receiver("jobs-max2", max_wait_time=5) as receiver:
    for _ in range(2):
        msg = receiver.receive_messages(max_message_count=1, max_wait_time=5)[0]
        receiver.abandon_message(msg)

    leftover = receiver.receive_messages(max_message_count=1, max_wait_time=5)
    print("active deliveries left:", len(leftover))                  # expect 0

with client.get_queue_receiver("jobs-max2", sub_queue=ServiceBusSubQueue.DEAD_LETTER, max_wait_time=5) as dlq:
    for dead in dlq.receive_messages(max_message_count=5, max_wait_time=5):
        print(dead.dead_letter_reason)                                 # MaxDeliveryCountExceeded
        dlq.complete_message(dead)
```

**Why / trap.** The broker dead-letters the message, not your code, once its delivery count passes `MaxDeliveryCount`. The reason is `MaxDeliveryCountExceeded`. The default limit is 10 (Learn, sessions article), so a lab that wants fast failure sets it low on purpose.

---

## Block 4 — Topic subscriptions: SQL filter, then correlation filter

**Q.** Create topic `events` with subscription `high` filtered by SQL (`priority = 'high'`) and subscription `all` with no filter. Publish three mixed-priority messages, check what each subscription receives, then swap `high` to a correlation filter.

```python
from azure.servicebus.management import CorrelationRuleFilter, SqlRuleFilter

try:
    admin.create_topic("events")
except ResourceExistsError:
    pass
for name in ("high", "all"):
    try:
        admin.create_subscription("events", name)
    except ResourceExistsError:
        pass

admin.delete_rule("events", "high", "$Default")                    # drop the match-everything rule
admin.create_rule("events", "high", "sql-high", filter=SqlRuleFilter("priority = 'high'"))

with client.get_topic_sender("events") as sender:
    sender.send_messages([
        ServiceBusMessage("a", application_properties={"priority": "high"}),
        ServiceBusMessage("b", application_properties={"priority": "low"}),
        ServiceBusMessage("c", application_properties={"priority": "high"}),
    ])

for name in ("high", "all"):
    with client.get_subscription_receiver("events", name, max_wait_time=5) as receiver:
        got = [b"".join(m.body).decode() for m in receiver.receive_messages(max_message_count=5, max_wait_time=5)]
        print(name, got)                                             # high ['a', 'c'], all ['a', 'b', 'c']

admin.delete_rule("events", "high", "sql-high")
admin.create_rule("events", "high", "corr-high", filter=CorrelationRuleFilter(properties={"priority": "high"}))
```

**Why / trap.** Every new subscription starts with a `$Default` rule that matches everything. If you add a SQL rule and forget to delete `$Default`, `high` receives `b` as well. A SQL filter is an expression evaluated per message. A correlation filter is an exact match on properties, which is the efficient choice when equality is all you need (Learn, topic-filters article; not re-fetched here). Re-running the block adds messages to `all`, so run it once per namespace.

---

## Block 5 — Modes: PeekLock vs ReceiveAndDelete

**Q.** Contrast the two receive modes. Which one is at-most-once, and when is that acceptable?

```python
from azure.servicebus import ServiceBusReceiveMode

with client.get_queue_receiver("jobs", receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE, max_wait_time=5) as receiver:
    for msg in receiver.receive_messages(max_message_count=1, max_wait_time=5):
        print("removed on read:", msg.message_id)                     # nothing to settle in this mode
```

**Why / trap.** **ReceiveAndDelete** removes the message the moment it is read. If the worker crashes before processing, the message is gone, so the mode is **at-most-once**. That fits fire-and-forget telemetry you can afford to lose. It does not fit article jobs. The enum members are `PEEK_LOCK` and `RECEIVE_AND_DELETE`.

---

## Block 6 — Extras to name-drop: sessions, scheduled, duplicates, auto-forward

**Q.** Name each extra and the setting that turns it on.

```python
from datetime import datetime, timedelta, timezone

# Sessions: one receiver holds a session_id at a time, and its messages come out in order
admin.create_queue("jobs-session", requires_session=True)
with client.get_queue_sender("jobs-session") as sender:
    sender.send_messages(ServiceBusMessage("step-1", session_id="article-42"))
with client.get_queue_receiver("jobs-session", session_id="article-42", max_wait_time=5) as receiver:
    for msg in receiver.receive_messages(max_message_count=10, max_wait_time=5):
        receiver.complete_message(msg)

# Scheduled: hidden from receivers until the UTC time you give
with client.get_queue_sender("jobs") as sender:
    sender.schedule_messages(ServiceBusMessage("retry-later"), datetime.now(timezone.utc) + timedelta(minutes=5))

# Duplicate detection: a repeated message_id inside the window is dropped
admin.create_queue("jobs-dedupe", requires_duplicate_detection=True,
                   duplicate_detection_history_time_window=timedelta(minutes=10))

# Auto-forwarding: messages move to another entity in the same namespace
admin.create_queue("jobs-archive")
admin.create_queue("jobs-forwarded", forward_to="jobs-archive")
```

**Why / trap.** Sessions change the contract: once a queue requires sessions, senders must set `session_id` and receivers must accept a session. Scheduled messages delay delivery, while TTL controls expiry, not start time. Duplicate detection keys on `message_id` and works only inside its window. Auto-forwarding is routing, not dead-lettering.

---

## Done-when check

**Q.** Name the four dead-letter triggers, then argue Service Bus versus Event Grid in two sentences.

**A.** The four triggers are: TTL expiry (only when dead-lettering on expiration is enabled), `MaxDeliveryCount` exceeded, an explicit dead-letter, and a subscription filter evaluation exception (only when dead-lettering on filter errors is enabled). Service Bus is a **pull** queue of commands that each consumer settles one by one. Event Grid **pushes** small facts to HTTPS handlers, and Service Bus queues and topics are among those handlers.

Cleanup: `floci az stop`.
