# Selecting an architectural style

Use these original decision heuristics with actual constraints. A style name does not establish quality. Book coverage and access limits are in [sources.md](sources.md).

| Candidate | Consider when | Costs and traps | Evidence to require |
|---|---|---|---|
| Simple single application | A small team owns a bounded product and releases it together | Implicit boundaries decay; runtime resources and failures are shared | Module responsibilities, representative load, recovery path |
| Layered architecture | Separating presentation, application behavior, and persistence clarifies dependencies | Bypassed layers; scattered changes; technical grouping hides business ownership | A use-case trace, transaction boundary, and representative change |
| Modular monolith | Capabilities need boundaries while local transactions and one deployment remain useful | Shared writes and cycles undermine boundaries; runtime resources remain shared | Data ownership, module APIs, dependency rules, isolated tests |
| Microkernel/plugins | A stable host needs controlled extension points | Contract drift, lifecycle issues, dependency conflicts, untrusted extensions | Versioned plugin contract, capabilities, error isolation, upgrade example |
| Microservices | Capabilities need independent release, ownership, scaling, or failure boundaries worth the distribution cost | Network failure, cross-service consistency, operational duplication, coordinated releases | Stable ownership, automation, observability, recovery plans, demonstrated independence needs |
| Event-driven architecture | Work can complete asynchronously and consumers can evolve within explicit contracts | Duplicates, disorder, stale views, poison messages, hidden dependencies | Delivery semantics, schema evolution, idempotent effects, backlog/replay controls, completion visibility |
| Ports and adapters | Domain policy should be testable independently of UI, provider, or persistence | Excess interfaces and translations obscure simple behavior | Actual boundary change pressure and adapter contract tests |
| Pipe and filter | Processing is a natural series of transformations | Bottlenecks, incompatible intermediate data, materialization cost, side-effect retries | Stage contracts, bounded buffers, error handling, reproducible input/output |

The last two rows supplement the inspected book topic map; do not attribute them to unread chapters.

## Separate deployment from modularity

Identify capability and data boundaries before deciding which need a process, network, or security boundary. A modular monolith may use asynchronous workers. Event-driven behavior may exist in one deployment. A service may have layered or ports-and-adapters internals. Explain combinations instead of treating all labels as exclusive choices.

## Check the distribution burden

- Which capability must deploy or scale independently now?
- Can an accountable team own its contract, data, deployments, and incidents?
- What happens when a network request fails after an external effect succeeds?
- How are cross-boundary workflows completed and reconciled?
- Can the team diagnose requests and roll out compatible contract changes?
- Does isolation gained justify coordination and operating costs?

Do not justify services using future user counts alone. Tie boundaries to a demonstrated or mandatory need.

## Evolve through an explicit seam

Give a likely extraction candidate an owned API and data boundary now; extract it when measured contention or delivery needs justify the cost. First prove clients can use its contract without accessing internals.

Plan ownership transfer, historical reconciliation, mixed-version operation, observability, cutover, and rollback. A new network boundary changes failure semantics; it is not merely a file move.

Reject options by mechanism: locality failure, unacceptable on-call load, missing expertise, or an invariant that cannot survive stated failures. Replace labels such as modern, enterprise-grade, and overkill with concrete consequences.
