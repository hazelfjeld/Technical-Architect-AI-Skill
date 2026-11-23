# Validation record

Date: **2026-11-23**

## Scope

Validated the installable skill's structure and local links, exercised the option evaluator in the initial build, and ran three realistic tasks in fresh agent contexts across two revisions. The solving agents received the skill and task inputs without the grader's acceptance criteria or an intended answer.

Trials A and B apply to the initial runtime recorded in [initial-skill-snapshot.json](evals/initial-skill-snapshot.json). After reviewing all extracted text of the supplied Design Patterns PDF, the main skill and pattern reference gained behavioral-contract probes, and the source records were updated. Trial G exercises that revision, recorded in [skill-snapshot.json](evals/skill-snapshot.json). Trials A and B were not rerun after these instruction changes. The option evaluator is byte-for-byte unchanged from its tested version.

## Mechanical checks

| Check | Observed result |
|---|---|
| Skill creator's bundled `quick_validate.py` on the canonical skill directory | Passed: valid frontmatter and skill structure |
| Relative Markdown references inside the skill | All referenced local files exist |
| Source manifest | Valid JSON; 17 unique source IDs; separate retrieval, text-review, and visual-inspection status |
| Supplied PDF record | Artifact byte size and SHA-256 matched; reading ranges cover PDF pages 1-672 exactly once; 13 visual pages listed |
| Runtime distribution | Four changed files match the canonical installed skill; snapshot records all 16 distribution files |
| Option comparison utility, initial build | 17 unit tests passed |
| Distributed copy of the utility and tests, initial build | Same 17 tests passed from the repository root; utility unchanged in this update |

The structure check verifies packaging conventions, not architectural competence.

## Reproduce the utility checks

Run from the repository root with Python 3.10 or newer:

```bash
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
python3 technical-architect/scripts/evaluate_options.py \
  technical-architect/assets/option-matrix.example.json
```

The 17 tests cover weighted arithmetic, hard-constraint precedence, provisional unknowns, failed-versus-unknown precedence, missing/extra assessments, nonempty evidence, duplicate IDs and JSON keys, booleans and invalid numbers, large/extreme weights, explicit assumptions, version validation, stable ties without premature rounding, an explicit empty-constraint case, the hypothetical example, and CLI behavior.

The example ranks only the eligible modular-monolith option; the separate-services option remains provisional because a hard budget constraint is unknown. These are illustrative judgments, not measurements or a universal style ranking.

## Behavioral trial A: small-team SaaS

Input: two developers, six weeks, 500 expected users, a $150 monthly budget, exclusive appointment slots, photos, administration, and nightly reports.

Observed output: [complete response](evals/responses/saas-architecture.md), 1,030 whitespace-delimited words.

| Criterion | Assessment |
|---|---|
| Constraints drive the design | Met: explicitly uses team size, delivery window, and budget |
| Credible alternatives and a simple baseline | Met: compares a managed monolith, VPS alternative, and services/Kubernetes |
| Booking invariant and failure behavior | Met: durable uniqueness, transaction boundaries, idempotency, and conservative recovery |
| Evidence honesty | Met: workload and vendor feasibility are assumptions; budget figures are caps, not verified prices |
| Ownership, uploads, async work, and operations | Met: scoped modules and data, authorized uploads, report recovery, operational roles |
| Decision and delivery | Met: proposed ADR, three slices, acceptance checks, and revisit conditions |
| No fabricated implementation/testing claims | Met: distinguishes proposed tests from actual verification |

Assessment: **met the case criteria**. No live system was changed. Current primary documentation was consulted where the response used framework/database facts.

## Behavioral trial B: invoice-service review

Input: the [synthetic billing fixture](evals/fixtures/billing-service/README.md), eight workers, queue redelivery, and a provider whose idempotency records expire after 48 hours.

Observed output: [complete response](evals/responses/invoice-review.md), 1,072 whitespace-delimited words.

| Criterion | Assessment |
|---|---|
| Evidence-backed findings | Met: references inspected paths and symbols |
| Process-local state limitation | Met: identifies independent processes, restart loss, and initialization resets |
| Timeout-after-effect ambiguity | Met: stable operation identity and immutable request data |
| Provider retention boundary | Met: prevents claims of indefinite retry safety and explains unresolved outcomes |
| Data/event publication gap | Met: paid-plus-outbox transaction, relay recovery, and fulfillment deduplication |
| Remote effect atomicity | Met: explicitly states the outbox does not make the payment provider atomic with the database |
| Remediation and verification | Met: durable state, reconciliation, ordered slices, and failure-case checks |
| Limits of evidence | Met: separates fake reproductions from integration guarantees |

The reviewing agent reported targeted checks on unchanged fixture code using fakes: eight charge calls for one invoice across eight processes; two successful charges after an ambiguous timeout; and two charges after publication failure followed by redelivery. These checks support the defect findings. They do not validate the proposed remediation against a real provider.

Assessment: **met the case criteria**. No production access or service modification occurred.

## Behavioral trial G: job-status contracts

Input: the original [job-status fixture](evals/fixtures/job-status/README.md), with current authorization and freshness requirements plus synchronous, reentrant progress subscribers.

Observed output: [complete response](evals/responses/job-status-review.md), 857 whitespace-delimited words.

| Criterion | Assessment |
|---|---|
| Authorization across the wrapper | Met: identifies revocation and different-actor bypass on cache hits; actor-specific keys are insufficient |
| Freshness contract | Met: indefinite caching violates latest committed status; a TTL does not satisfy exact freshness |
| Notification snapshots and ordering | Met: traces reentrant delivery as A receiving `[1, 2]` and B receiving `[2, 2]`; proposes immutable payloads and a non-reentrant FIFO drain |
| Exceptions and subscriber lifetime | Met: identifies exception starvation and self-removal skipping the next subscriber; specifies per-event membership and isolation |
| Smallest adequate design | Met: retains live reads and a local notification queue; identifies concurrency as an unresolved contract question |
| Evidence and verification limits | Met: cites inspected symbols and separates executed defect reproductions from proposed remediation checks |

The reviewing agent executed local fake probes against the unchanged fixture and reproduced all five findings. Its proposed correction was not implemented or integration-tested. No network service or production system was accessed.

Assessment: **met the case criteria**. This checks the updated pattern guidance on one focused task; it does not establish a causal performance improvement or general architectural expertise.

## Limits

- Three task trials across two revisions are a small qualitative sample. They do not prove general expert-level performance, improvement over a baseline, or reliability on every architecture task.
- The four additional cases in [cases.md](evals/cases.md) are future regression prompts; they were not executed in this build.
- The option utility validates input and arithmetic. It does not verify the truth of evidence, completeness of constraints, workload estimates, or production correctness.
- Software Architecture remains partially inspected. The complete Design Patterns PDF was retrieved and all extracted text reviewed, with 13 selected visual-page checks. Exercises were not independently completed and publisher code was not executed. See the [source guide](technical-architect/references/sources.md).
- No cloud deployment, real payment, production load test, or external side effect was performed by the behavioral trials.
