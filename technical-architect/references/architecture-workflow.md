# Architecture workflow

Use this original procedure to turn uncertain goals into decisions with testable consequences. The book-access record is in [sources.md](sources.md); this is not a chapter summary.

## Frame the decision

Write: **Achieve [outcome] for [users] within [constraints], while protecting [invariants].**

Identify whether the question concerns a whole system, a deployment boundary, a data owner, an integration, or a local variation point. A local defect rarely warrants redesigning the whole application.

| Evidence item | Status | Source | Consequence if wrong |
|---|---|---|---|
| Requirement or behavior | Verified / required / assumed / unknown | User statement, file and symbol, measurement, or primary documentation | Which choice changes |

Resolve an unknown if it could eliminate an option, expose an irreversible cost, or change the first implementation slice. Defer questions that cannot affect the current choice.

## Express quality scenarios

Replace fast, secure, scalable, and maintainable with scenarios. Numbers below are illustrative proposed targets, not defaults or measurements.

| Quality | Scenario | Verification |
|---|---|---|
| Latency | At a stated peak workload, 95% of cached product-page responses complete within a proposed 300 ms | Measure end-to-end latency, cache state, and dependency contributions |
| Changeability | A new shipping rule changes one owned policy module and its tests without editing checkout orchestration | Implement a representative change and inspect the diff |
| Recovery | A worker exits after accepting a task; pending work resumes without duplicate external effects | Terminate the worker at relevant boundaries and reconcile durable state |
| Isolation | A tenant requests another tenant's object; all access paths deny disclosure | Exercise API, background job, export, and cache paths |
| Deployability | Old and new versions overlap during a schema change without corrupting state | Rehearse mixed-version operation and verify rollback limits |

Specify load shape, dataset size, concurrency, geography, freshness, and failure conditions when relevant. Name the person or role that accepts each target.

## Find boundaries through invariants

Ask which facts each capability owns, which rules must hold atomically, which changes occur together, who operates it, and what other capabilities may read or modify.

| Capability | Owner | Authoritative data | Invariants | Public contract | Dependencies |
|---|---|---|---|---|---|
| Named capability | Team or module | Entities and lifecycle | Conditions that remain true | Commands, queries, events | Protocol and failure behavior |

Separate logical ownership from physical storage. Modules may share a database server while enforcing ownership. Separate processes may remain tightly coupled through shared writes, synchronized releases, or long request chains.

Inspect imports, direct table access, transaction scopes, deployments, and critical traces. Treat dependency cycles as evidence to investigate, not proof that services are needed.

## Make diagrams answer a question

- Use a context view for users, the system boundary, and external systems.
- Use a component/deployment view for executable units, storage ownership, and communication.
- Use a dynamic view for ordering, branches, partial failure, and compensation in one critical journey.
- Use a data view for authoritative entities, consumers, and replication direction.

Label edges with purpose and protocol. Mark current/proposed state and trust boundaries. Explain any mixing of classes, hosts, and capabilities at different abstraction levels.

## Compare options transparently

Start with hard constraints and a minimal baseline. Include implementation time, operational load, recovery burden, and future change cost alongside runtime qualities.

| Option | Constraints | Scenario fit | New burden | Evidence/confidence | Decision |
|---|---|---|---|---|---|
| Current or simplest credible design | Pass / fail / unknown per constraint | Explain mechanism | People, infrastructure, coordination | Measurement, code, or explicit assumption | Keep / reject / investigate |

Use `scripts/evaluate_options.py` with its module documentation and example JSON when arithmetic is useful. It validates structure and calculates scores; it cannot verify evidence or approve a design. A failed constraint cannot be compensated by a high preference score.

For close rankings, vary plausible weights and challenge speculative scores. Prefer a rationale that survives uncertainty, or run a targeted experiment before committing.

## Bound experiments and decisions

Specify a hypothesis, representative workload, acceptance threshold, maximum effort, owner, and how the result changes the decision. A successful toy benchmark does not establish production capacity. Report the environment, dataset, cache state, failure conditions, and relevant differences.

Use an ADR for consequential choices. Preserve alternatives and accepted disadvantages. Supersede prior decisions with links rather than silently rewriting their history.

Define observable revisit triggers such as deployment contention, measured latency failure, independent ownership, or contractual requirements. Close with the smallest buildable slice and the check that proves its outcome.
