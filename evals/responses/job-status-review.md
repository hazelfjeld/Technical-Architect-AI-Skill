# Job-status release review

**Recommendation: hold release of both proposed components until the five contract failures below are fixed.** Retain `LiveStatusProvider` for reads and implement a small serialized notification loop for `ProgressFeed`; this one-process scope needs no broker, persistence layer, or class hierarchy.

Scope: `evals/fixtures/job-status/README.md` and `evals/fixtures/job-status/status.py`. The README requires authorization on every read, latest committed status, ordered immutable revision snapshots, and subscriber isolation. Findings below are visible in source **and reproduced with local fakes**. No fixture files or live systems were changed. No committed revision identifier was available (`git rev-parse HEAD` failed).

## Findings, ordered by impact

### 1. High — Cache hits bypass access control

**Evidence:** `evals/fixtures/job-status/status.py`, `CachedStatusProvider.read`, calls `LiveStatusProvider.read` only on a miss; the latter owns `_authorize`. `_cache` is indexed solely by job ID.

**Trigger/consequence:** After Alice warms a job, revoking Alice or requesting it as unauthorized Bob still returns the cached status without authorization. Both cases reproduced; direct live reads rejected both actors. Globally unique job IDs prevent collisions, but do not grant access.

**Smallest correction:** Stop caching at this wrapper and delegate every read to the live provider. If optimization is later necessary, introduce an explicit authorized read contract that always checks current access. Adding actor IDs to cache keys still fails revocation.

**Verification:** Warm a job, revoke that actor, and assert denial on the next read. Also assert that a different denied actor cannot read the warmed job and that authorization executes on every call.

### 2. High — Cached status never becomes current again

**Evidence:** `evals/fixtures/job-status/status.py`, `CachedStatusProvider.read`, has no invalidation, version check, or refresh after insertion.

**Trigger/consequence:** Updating the fake authoritative store from revision 1 to 2 made `LiveStatusProvider` return 2 while the cache still returned 1. Progress may remain permanently stale, including after completion.

**Smallest correction:** Use the same unconditional delegation as finding 1. This preserves correctness at the cost of the proposed read savings. A future cache requires either authoritative revision validation or synchronous invalidation covering **every** writer before a committed update becomes visible. No such write integration is supplied; a TTL cannot satisfy the exact freshness requirement.

**Verification:** Commit successive statuses through every authoritative update path and assert that each subsequent successful read returns the newest revision, including across actors.

### 3. High — Reentrant commits lose revision snapshots and ordering

**Evidence:** `evals/fixtures/job-status/status.py`, `ProgressFeed.commit`, changes shared `current`, recursively dispatches, and passes the mutable feed to callbacks.

**Trigger/consequence:** Subscriber A commits revision 2 while handling revision 1. The executed trace was A: `[1, 2]`, B: `[2, 2]`; B never observes revision 1. Snapshotting only the subscriber list does not fix this.

**Smallest correction:** Queue each immutable `Status` with its subscriber snapshot. Use one guarded, non-reentrant FIFO drain and pass the queued `Status` directly to callbacks; subscribers can retain the feed reference for commits and removal. Keep `current` at the latest committed revision rather than rewinding it during delivery. Define nested `commit` as accepting/enqueuing immediately, with notification occurring after the current revision finishes delivery. This adds a small queue and changes the proposed callback contract.

**Verification:** Assert the trace `A1, B1, A2, B2`, exact snapshot values, and unchanged revision-1 payloads after revision 2 commits.

### 4. High — One subscriber exception suppresses all following notifications

**Evidence:** `evals/fixtures/job-status/status.py`, `ProgressFeed.commit`, calls subscribers without an exception boundary.

**Trigger/consequence:** An executed raising first subscriber prevented the healthy second subscriber from running although `current` had already committed revision 1. The caller receives an error after mutation, and subscribers disagree about observed progress.

**Smallest correction:** Isolate ordinary exceptions per callback, report failures through a defined diagnostic hook, and continue delivering to remaining subscribers and queued revisions. Reset the drain guard in `finally`; subscriber failure must not roll back committed state or strand future events.

**Verification:** Make the first and middle callbacks raise, including after enqueuing a newer revision. Healthy subscribers must receive every queued snapshot in order, and a subsequent commit must still dispatch.

### 5. Medium — Self-removal skips the next subscriber

**Evidence:** `evals/fixtures/job-status/status.py`, `ProgressFeed.unsubscribe`, mutates the same list iterated by `commit`.

**Trigger/consequence:** With subscribers A, B, C, A removing itself produced only A and C in the executed trace.

**Smallest correction:** Capture `tuple(self._subscribers)` per committed event, as in finding 3. Define membership at commit time: removal affects future commits, while already queued events retain their recipient set. This makes callback lifetime predictable at the cost of retaining references until queued delivery completes.

**Verification:** A self-removal must preserve B and C's current-revision notifications; A must be absent from revisions committed after removal.

## Release sequence and limits

The component owner should first restore correct reads, then implement queued snapshot delivery with stable membership and exception isolation, and run the focused checks above before release. Clarify whether multiple threads may call the feed; the supplied one-process requirement alone does not establish thread safety, and the proposed drain needs synchronization if concurrent callers are supported. The expensive-read workload and a safe invalidation protocol remain unmeasured.

**Executed:** `python -B /tmp/job-status-review-probes-8254.py` reproduced all five defects using local fakes. These were reproduction checks against the original implementation, not validation of fixes. No remediation, concurrency test, benchmark, durable-delivery test, or production check was performed; crash recovery is explicitly outside scope.
