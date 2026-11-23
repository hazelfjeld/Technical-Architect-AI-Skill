# Appointment-booking SaaS: proposed architecture

**Build a modular monolith: Django, PostgreSQL, private object storage, and a scheduled worker from the same codebase.** Use one managed application platform and one region. Defer Kubernetes and feature microservices: independent deployment is not yet a requirement, while reliable booking and six-week delivery are.

## Constraints and assumptions

**Given:** two developers, six weeks, approximately 500 users, $150/month, exclusive slots, photos, administration, and nightly reports.

**Assume:** 500 registered users, 20 concurrent users, 10 requests/second peak; familiarity with Django; predefined, nonoverlapping, single-capacity slots; no payments, temporary holds, or regulated records. Budget for 10 GB of photos and 50 GB/month of downloads. These are planning assumptions, not measured demand.

**Proposed acceptance targets:** booking p95 below 500 ms at that load; zero double bookings under concurrent requests and retries; reports available by 06:00 in each tenant’s timezone. Correctness takes precedence over booking availability.

## Concrete design and spending limits

| Component | Responsibility and boundary |
|---|---|
| Django web process | Server-rendered customer pages and HTTPS endpoints; authentication, authorization, booking commands, upload authorization, report downloads |
| PostgreSQL primary | Authoritative slots, bookings, users, upload metadata, command receipts, and report runs; all confirmations use this primary |
| Private object storage | Photo bytes and report files; browsers upload through narrowly scoped, short-lived signed requests |
| Scheduled worker | Same repository/image, separate process; validates photos and produces reports without occupying web requests |

Keep `accounts`, `booking`, `media`, and `reporting` modules. Booking owns slot and reservation writes; other modules and admin actions call its functions. Reporting reads approved queries and owns its derived results. Use Django admin for internal staff; tenant administrators receive explicitly scoped views. Django documents its admin as an internal management interface.[1]

**Monthly allocation caps, not verified vendor prices:** application/worker/scheduler $40; managed PostgreSQL including backups $65; storage/traffic $15; monitoring and transactional email $10; contingency $20. Total: **$150**. Actual feasibility remains unverified; obtain current quotes including staging, backup retention, egress, and taxes in week one. Apply upload quotas and budget alerts.

## Booking data and failure behavior

Store `slots(tenant_id, id, resource_id, starts_at, ends_at)` and `bookings(id, tenant_id, slot_id, customer_id, cancelled_at)`. Require non-null identities and a composite foreign key enforcing matching tenant and slot. Store instants in UTC and retain the business’s IANA timezone.

Enforce the invariant in PostgreSQL:

```sql
CREATE UNIQUE INDEX one_active_booking_per_slot
ON bookings (tenant_id, slot_id)
WHERE cancelled_at IS NULL;
```

PostgreSQL supports partial unique indexes and resolves conflicting concurrent inserts against transaction outcomes.[2][3] Prevent overlapping slot definitions for the same resource with a range exclusion constraint; freeze a slot’s time once booked.[2]

`POST /bookings` authorizes the tenant/customer, locks the slot row, validates eligibility, and inserts the booking plus command receipt in one transaction. Only acknowledge success after commit. A conflicting booking returns `409`; a displayed available slot is never a reservation. Cancellation releases the claim transactionally; rescheduling cancels and creates atomically, rolling back both if the destination is unavailable.

Scope an idempotency key to tenant, customer, and operation. Persist its request hash and outcome with the booking; retain receipts for the booking’s lifetime. Reusing the key with different input fails. A timeout after commit is an **unknown outcome**: retry the same key or retrieve its receipt. Database uncertainty stops confirmations; never infer success from cache or memory.

For disaster recovery, require documented backup guarantees and rehearse restoration; propose recovery within four hours and a backup-loss window of at most 15 minutes, subject to budget validation. If recovery might omit acknowledged bookings, quarantine every future slot that could have been booked during the lost interval until reconciled or expired. A stale backup must not silently reopen inventory.

## Photos, reports, and operations

Create tenant-owned upload records and random object keys. Limit uploads to 5 MB, validate decoded image type/dimensions, re-encode, and publish only validated objects. Serve through authorized downloads; delete abandoned uploads after 24 hours. Storage failure leaves photos pending and booking available.

The scheduler discovers missing report dates, including after downtime. A unique `(tenant_id, business_date, report_version)` identifies each run. Workers use expiring claims, bounded retries, and conditional completion so a stale worker cannot publish over its replacement. Write immutable output, then atomically record its pointer. Retries may compute twice; expose one completed report. Display failures and last-success time; alert the operations owner after exhausted retries or a missed deadline.

Enforce tenant scope on API, admin, storage, and report paths. Use HTTPS, secure sessions, CSRF protection, and staff MFA. Developer A owns booking correctness; Developer B owns operations. Monitor latency, errors, job age, backup freshness, and spend; cap report concurrency and query duration to protect bookings.

## Alternatives and short decision record

**ADR-001 — Proposed, 2026-11-23; owners: both developers.**

| Option | Decision and tradeoff |
|---|---|
| Managed modular monolith | Preferred: local transactions and one release pipeline; shared database and release failures remain the strongest downside. Budget fit requires quotes. |
| Monolith on a small VPS | Credible fallback if managed hosting misses the cap; developers inherit patching, process supervision, backup, and recovery work. |
| Kubernetes plus microservices | Defer: independent scaling and releases have value, but add network failures, service contracts, and operating responsibilities within this deadline. |

Revisit after measured contention persists despite indexing and worker limits, or separate teams require independent releases. Scale web/worker processes first; extract a capability only with evidence and explicit data ownership.

## First three implementation slices

1. **Weeks 1–2 — Customer books safely.** A builds schema/transaction/receipts; B builds login and booking UI. Obtain budget quotes. Acceptance: 100 simultaneous attempts yield one active booking; repeated keys and a lost commit response recover the same result. Use real PostgreSQL.
2. **Weeks 3–4 — Staff manages bookings; customer uploads a photo.** A implements cancellation/rescheduling; B implements scoped admin and media. Verify cross-tenant denial, failed reschedule preserving the original, invalid uploads, and orphan cleanup. Depends on slice 1.
3. **Weeks 5–6 — Operator receives nightly reports and can recover service.** B implements scheduling/alerts; A implements report queries and recovery procedures. Verify duplicate scheduling, worker crashes, missed-run catch-up, load targets, and backup restoration with quarantine. Depends on slices 1–2; reserve the final week for fixes.

### Sources

[1] [Django admin documentation](https://docs.djangoproject.com/en/stable/ref/contrib/admin/).

[2] [PostgreSQL constraints](https://www.postgresql.org/docs/18/ddl-constraints.html).

[3] [PostgreSQL concurrent uniqueness checks](https://www.postgresql.org/docs/18/index-unique-checks.html).
