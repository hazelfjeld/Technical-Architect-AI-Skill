# Invoice service architecture review

**Recommendation: do not deploy the current proposal with eight workers.** Keep one service, backed by shared transactional persistence, and add durable payment operations, provider idempotency, and an outbox. The provider’s 48-hour guarantee also imposes a recovery constraint that the current contract cannot fully resolve.

## Findings, ordered by impact

### 1. High — repeated processing can produce multiple successful charges

`InvoiceWorker` keeps its singleton and `seen` set in process memory (`billing.py:2`, `billing.py:13`). Eight processes have independent copies; restarts lose them, and another construction resets `seen`. `handle()` retries timeouts without supplying the supported `operation_key` (`billing.py:20`, `billing.py:22`). The README expressly permits both queue redelivery and a timeout after a successful charge (`README.md:3`, `README.md:5`).

**Consequence:** simultaneous deliveries, lost acknowledgments, and ambiguous timeouts can charge the same invoice repeatedly. An isolated eight-process check produced **eight charge calls for one invoice**. A fake provider that completed its first charge before timing out produced **two successful charges** from one handler invocation.

**Correction:** persist one payment operation per invoice under a database uniqueness constraint, with one stable provider key and immutable charge arguments. Every allowed retry must use that exact operation. Reject conflicting inputs rather than silently changing the amount or customer.

### 2. High — a committed payment has no durable fulfillment obligation

`handle()` calls `mark_paid()` before `events.publish()` (`billing.py:30`, `billing.py:31`); `mark_paid()` commits independently (`storage.py:16`). No pending-event record exists (`storage.py:5`). A crash or publication failure leaves payment recorded without a recoverable event. Redelivery follows the charging path again; `mark_paid()` overwrites the earlier receipt (`storage.py:4`). A fake publication-failure/redelivery check reproduced two charges with only the second receipt retained.

**Correction:** commit confirmed payment state and a uniquely identified outbox event in one transaction. A recoverable relay publishes it with retries. Publication may succeed before its acknowledgment is recorded, so fulfillment must deduplicate repeated events atomically with its own effect. A paid-status guard alone would prevent recharging while leaving the event gap unresolved.

### 3. High — unknown outcomes lack safe recovery, especially after 48 hours

Exhausted timeouts simply raise (`billing.py:26`); storage has no operation record (`storage.py:5`). The provider remembers identical keyed requests for only 48 hours (`README.md:5`). Adding a key alone therefore does not establish indefinite retry safety.

**Correction:** durably distinguish pending, unknown, confirmed-paid, and definitive-failure outcomes. Record the first submission boundary before calling the provider. Stop automatic charging when safe deduplication can no longer be established; neither the old key nor a replacement key is safe to submit blindly. Preserve the operation until trustworthy provider evidence resolves it.

**Contract limitation:** no provider lookup or permanent uniqueness guarantee is specified. Strict at-most-one charging plus eventual recovery across indefinitely ambiguous outcomes is therefore unproven. A paused worker can also resume after another worker’s successful attempt has aged past retention: a lease or database fencing token cannot prevent that external charge. Safe retry/takeover requires a verified bound on possible submissions, including stale requests, or stronger provider enforcement. Otherwise, retain an unresolved operation and forbid further charging.

## Smallest sound remediation design

Assume one logical payment per invoice and a shared database capable of transactions, uniqueness constraints, and conditional updates. Verify those capabilities before choosing an implementation; the fixture does not identify its database or deployment topology.

Keep `InvoiceWorker` as an ordinary injected worker. The service owns invoices, payment operations, and outbox rows; the provider owns charge execution, and fulfillment owns its deduplication and fulfillment transaction.

1. **Register and claim work.** Atomically create/load a uniquely constrained invoice operation containing its stable key, exact request fields, state, receipt, and timestamps. Validate invoice existence and input consistency before submission. Conditional claims coordinate workers; expired claims must not automatically authorize unsafe resubmission.
2. **Execute and recover charging.** Call the provider outside the database transaction using persisted inputs. Use bounded retries with backoff only inside a conservatively established safe window. Record ambiguous outcomes; never interpret a timeout as proof of failure. A local timeout alone does not cancel a remote charge.
3. **Finalize atomically.** On confirmed success, transactionally transition the operation and invoice to paid and insert one `invoice.paid` outbox row, uniquely constrained by operation and event type. Preserve the confirmed receipt; conflicting receipts require reconciliation. This transaction solves local state/event consistency, not atomicity with the provider.
4. **Deliver and deduplicate.** Relay outbox rows using stable event IDs; mark delivery only after durable destination acknowledgment. Fulfillment records each ID with its business update in one transaction. Any further external fulfillment effect needs its own idempotency contract. Acknowledge input messages only after durable recovery responsibility exists; provide a scanner for unfinished operations and outbox rows.

**Alternatives:** a process singleton, distributed lock alone, or paid-status check fails the demonstrated recovery paths. A shared database plus an outbox is the smallest credible change. A separate workflow platform adds operational cost without removing the provider’s retention boundary; reconsider it only if broader workflows justify that cost. The preferred design’s main cost is schema, recovery, and relay ownership.

## Initial implementation slices

| Order and owner | Scope and acceptance |
|---|---|
| **1 — Billing engineer: durable payment identity** | Extend `storage.py` and replace `seen` in `billing.py`. Add unique operations, immutable inputs, guarded transitions, and keyed calls. Eight simultaneous deliveries produce one successful provider effect; conflicting input is rejected; redelivery returns the persisted outcome. |
| **2 — Billing/provider owner: ambiguity recovery** | Add unknown-state recovery, submission deadlines, and stale-worker handling under a verified provider contract. Exercise timeout-after-success and crashes before/after submission. After the safe window, assert zero new charge submissions and an actionable reconciliation record. |
| **3 — Billing and fulfillment owners: durable events** | Replace independent paid commits with paid-plus-outbox transactions; add relay and consumer deduplication. Inject crashes before/after commit, after publication, and before acknowledgments: confirmed payments eventually fulfill once when dependencies recover. |
| **4 — Operations owner: release gate** | Rehearse all failure cases with eight processes. Monitor unknown-payment age, oldest outbox age, retry volume, and reconciliation backlog. Set recovery-time targets from workload requirements; throughput and SLOs are currently unspecified. |

For any existing data, reconcile paid receipts and missing fulfillment before backfilling; never recharge to reconstruct events. Avoid mixed deployment with the old worker. Rollback must preserve durable operation identities and pending events.

**Review limits:** inspected all three supplied files; no deployment configuration, dependency manifest, or test suite was supplied. Executed targeted in-memory failure checks and an eight-process fake-provider check. These demonstrate current defects, not the proposed design’s integration guarantees. No service files were changed and no live systems were accessed.
