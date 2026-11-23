# Pattern selection and restraint

Use this original decision aid at the object or module level. For book coverage and official Java resources, see [sources.md](sources.md). This file is not a chapter-by-chapter substitute.

## Require a reason before a pattern

Record **observed pressure → stable contract → independent variation → simplest baseline → candidate → cost → validation → removal condition**.

Demonstrate one current behavior and one realistic change. Keep a plain function, branch, data table, iterator, or module when adequate. Justify each new abstraction in the target language and codebase.

## Select by the problem

These are general software-design heuristics, not quotations or book summaries. Source coverage and inspection limits are recorded separately in [sources.md](sources.md).

| Pattern | Pressure that may justify it | Simpler alternative and caution |
|---|---|---|
| Strategy | Algorithms share a useful contract and vary independently of orchestration | Inject a function first; avoid class hierarchies for a trivial branch |
| Observer | In-process subscribers react without the publisher naming each consumer | Direct calls may be clearer; define ordering, reentrancy, exceptions, and unsubscribe lifetime |
| Decorator | Behavior composes around a compatible contract | Prefer functions or middleware where idiomatic; expose order, duplicate effects, and debugging cost |
| Factory Method | A construction extension point supplies a product while a workflow stays stable | Use a constructor/factory function unless subclass customization helps |
| Abstract Factory | Related products must form a compatible family | Configuration may suffice; avoid speculative future families |
| Singleton | Exactly one controlled instance is needed within a defined scope | Prefer an injected process-scoped instance; globals hinder testing and do not enforce cross-process uniqueness |
| Command | A request needs representation for scheduling, history, or reversible work | A function may suffice; persistence, retries, authorization, and undo need separate design |
| Adapter | A boundary has incompatible contracts | A mapping function may suffice; translate errors, units, pagination, and cancellation as well as names |
| Facade | Clients need a coherent operation over a complicated subsystem | A module operation may suffice; avoid unrelated responsibilities and hidden transactions |
| Template Method | A stable ordered algorithm permits limited variation through inheritance | Consider composition; specify hook invariants and subclass obligations |
| Iterator | Traversal should hide representation behind clear access semantics | Prefer native iteration; define mutation, lazy I/O, ordering, and resource lifetime |
| Composite | Leaves and nested groups genuinely share useful operations | Use a simple tree where adequate; prevent invalid leaf operations and forbidden cycles |
| State | Legal behavior depends on lifecycle transitions | An enum plus transition table may suffice; define transition ownership, persistence, and invalid transitions |
| Proxy | An intermediary controls access, lifecycle, locality, or acquisition | Explicit calls may be clearer; expose remote latency and failure semantics |

## Broaden the search only if needed

Consider these additional conventional patterns only when the observed problem calls for them.

| Pattern | Consider for | Main burden |
|---|---|---|
| Builder | Construction with staged validation or coherent optional settings | Prevent incomplete objects escaping; prefer named arguments for simple records |
| Prototype | Copying a configured instance is the useful construction model | Define deep/shallow copy and mutable ownership |
| Bridge | Two abstraction dimensions truly vary independently | Require evidence for both dimensions |
| Flyweight | Repeated immutable values can share intrinsic state | Separate contextual state and measure lifetime/memory costs |
| Chain of Responsibility | Ordered handlers can process or pass requests | Define precedence, termination, and whether multiple handlers may act |
| Interpreter | A small stable language needs explicit evaluation | Consider parsers or data first; bound resource use |
| Mediator | Peer coordination has become a dependency web | Scope it to a workflow; avoid an all-purpose coordinator |
| Memento | Bounded state restoration is useful | Define size, sensitive fields, versions, and external-effect limitations |
| Visitor | Many operations traverse a stable set of element types | Changing types is costly; consider simple traversal or pattern matching |

## Resolve common confusions

- **Strategy/State:** policy selection versus lifecycle-driven behavior; define who owns transitions.
- **Adapter/Facade:** incompatible interface versus complicated interaction; translation and orchestration remain distinct responsibilities.
- **Decorator/Proxy:** composable behavior versus control over access or lifetime; judge intent and runtime semantics, not wrapper shape.
- **Factory Method/Abstract Factory:** one product's construction extension versus compatible product families. A simple factory function is not automatically GoF Factory Method.
- **Template Method/Strategy:** inheritance hooks versus replaceable collaborators; protect invariants with minimal coupling.

## Preserve system semantics

An Observer does not create durable delivery. A Command does not create a reliable queue. A Singleton does not deduplicate work across replicas. A Proxy does not make network calls local. A State object does not persist a recoverable workflow. Design data and failures explicitly at these boundaries.

## Probe the behavioral contract

Apply relevant probes to actual callers and state. These are original engineering review steps; they are not guarantees supplied by a pattern name.

- **Notifications:** Choose event snapshots or reads of current state. Trace a reentrant update, a failing subscriber, and listener removal; check versions and delivery order.
- **Wrappers:** Trace writes and reads through the outer object. Check state forwarding, inner-object escape, cache freshness, authorization on cache hits, and ordering of effects.
- **Shared instances:** Separate identity and lifetime from safe initialization, concurrent mutation, and disposal. Establish each property independently.
- **Commands:** Give each execution its own captured state and result. Exercise repeated invocation and partial failure; distinguish exact restoration from compensation.
- **State:** Map events to guards, effects, next states, and invalid outcomes. Name transition ownership; verify rejected events produce no forbidden effects.
- **Factories:** Probe a new family and a new product category. Record affected contracts and how family compatibility is enforced.
- **Composites:** Identify operations common to all nodes and branch-only capabilities. Choose explicit unsupported operations or narrower interfaces deliberately.
- **Composed designs:** Assign input handling, domain invariants, reads, and notifications to owners. Trace independent update paths; justify each added pattern.

## Prove the abstraction helps

Identify callers and preserved behavior. Show the smallest patch and dependency changes. Add a focused behavioral or contract check. Demonstrate the realistic change without rewriting unrelated callers. Record new types, runtime costs, and debugging steps. Simplify when the variation disappears or ordinary changes become harder.

Use original examples. Link official code instead of vendoring publisher examples without a suitable license.
