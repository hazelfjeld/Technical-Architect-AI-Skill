# Data, failure, and recovery design

Use this original engineering checklist only for relevant risks. These operational details supplement the inspected Head First materials; they are not attributed to unread chapters.

## Model the invariant before the transport

State what must never happen, which records represent the truth, and who may change them. Locate the atomic boundary. If an invariant crosses independent systems, identify how violations are prevented, detected, repaired, or accepted by the business.

Distinguish acceptance from completion. A queued request can be accepted while its business effect is still pending. Define the user-visible states, durable transitions, recovery owner, and reconciliation process.

## Specify contracts

For a command, query, or event, record:

- Caller identity, authorization scope, tenant context, and input validation.
- Schema, version, units, nullability, maximum size, and compatibility rules.
- Deadline, cancellation behavior, retryable errors, and completion semantics.
- Idempotency scope, key origin, retention, and behavior for key reuse with a different payload.
- Ordering requirements, freshness allowance, and correlation identifiers.
- Data classification, retention, deletion, and safe logging constraints.

Avoid one vague error path. Distinguish invalid input, forbidden access, conflict, throttling, dependency failure, and unknown outcome.

## Trace partial failure

| Failure | Questions to resolve | Candidate mechanisms to verify |
|---|---|---|
| Client times out after a side effect | Did the effect happen? Can the caller recover its result? | Stable operation identity, provider-supported idempotency where available, durable status, reconciliation |
| Database commit succeeds but event publish fails | How does downstream work become visible? | Transactionally stored outbox plus a recoverable relay; consumers still handle duplicates |
| Event is delivered again | Can a duplicate change state or charge twice? | Atomic effect/deduplication boundary, uniqueness constraints, idempotent operations |
| Worker crashes mid-task | Which state survives and who resumes work? | Durable progress, bounded leases, fencing where needed, retry policy, reconciliation |
| Events arrive out of order | Which transitions remain valid? | Version checks, per-entity sequencing, stale-event rejection, or order-independent operations |
| Consumer is slower than producers | What bounds growth and protects upstream resources? | Backpressure, admission control, bounded queues, scaling limits, load shedding |
| One dependency fails repeatedly | How is cascading work prevented? | Deadlines, bounded retries with jitter, concurrency limits, isolation, verified fallback |
| A task repeatedly fails | How is work recovered without an endless loop? | Attempt budget, quarantine/dead-letter handling, inspection owner, replay controls |

No mechanism guarantees success by name. An outbox does not make a remote payment atomic with a database update. A lease does not prevent a stale worker from acting after expiration unless the effect boundary rejects it. A dead-letter queue needs an owner and recovery process.

## Make retries safe

Retry only when the operation is safe to repeat or its effects can be reconciled. Keep the same logical operation identity across attempts. Bound retry count, total time, and concurrent work. Respect caller deadlines and dependency throttling. Avoid layered retries multiplying attempts.

For irreversible external effects, verify the provider's actual guarantees and retention windows in current primary documentation. If outcome remains unknown, preserve an explicit pending/unknown state and reconcile; do not invent a new key and blindly repeat the action.

For multi-step workflows, document compensation as a business operation with its own failure modes. Releasing reserved inventory may be possible while undoing a notification is not. A compensating action is not a database rollback.

## Choose consistency and storage deliberately

Name the source of truth per entity. Distinguish authoritative writes, derived views, caches, and analytics. State which reads require current state and which tolerate staleness. Define cache invalidation or expiry behavior and its consequences.

Prefer a transaction when the needed invariant and data fit one appropriate transaction boundary. Add distributed coordination only when boundaries justify it. Choose storage using access patterns, data shape, transactional needs, growth, operations, and recovery requirements; avoid selecting by trend.

Specify indexes and query costs where evidence warrants them. Estimate capacity with workload units: requests per second, bytes per record, retention period, peak concurrency, queue drain rate, and replication overhead. Show assumptions; benchmark the decisive uncertainty.

## Design security boundaries

Identify users, services, untrusted inputs, sensitive stores, and boundary crossings. Enforce authorization at the operation and resource boundary, including background jobs and exports. Carry tenant identity safely and verify isolation in queries, caches, logs, and storage paths.

Use least-privilege service credentials and explicit secret handling. Validate inputs and outputs at trust boundaries. Keep sensitive values out of diagnostics unless the project requires a controlled mechanism. Review current platform documentation for specific controls rather than inventing configuration keys.

## Define operations and recovery

Specify signals tied to outcomes: successful completions, end-to-end latency, error/unknown-result rates, queue age, retry volume, reconciliation backlog, and tenant isolation failures where applicable. Establish an owner and response for each actionable alert.

State proposed availability, recovery time, and acceptable data-loss targets separately. A backup is not a demonstrated recovery capability until restoration is rehearsed. Test the most consequential failure and explain what remains unverified.

## Migrate without losing the truth

Plan compatible schema expansion, bounded backfill, validation/reconciliation, switch of reads and writes, and eventual removal. Explain mixed-version behavior, concurrent updates, rollback conditions, and irreversible steps. A feature flag cannot restore destroyed data or undo an external effect.
