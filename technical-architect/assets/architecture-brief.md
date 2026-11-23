# Architecture brief: [system or decision]

Status: Proposed | Owner: [role] | Date: [date] | Scope/revision: [scope]

## Recommendation

[Decision, primary reason, accepted tradeoff, and next action.]

## Outcome, constraints, and evidence

| Item | Verified / required / assumed / unknown | Evidence | Consequence if wrong |
|---|---|---|---|
| [Business outcome or constraint] | [Status] | [Source] | [Decision affected] |

## Quality scenarios

| Quality | Stimulus and environment | Component and response | Target and evidence status | Verification |
|---|---|---|---|---|
| [Quality] | [Load or failure context] | [Required behavior] | [Measured / proposed] | [Check] |

## Responsibilities and data

| Capability | Owner | Authoritative data | Invariant | Contract |
|---|---|---|---|---|
| [Capability] | [Role/module] | [Data] | [Rule] | [API/event] |

[Add a focused diagram if it clarifies boundaries, topology, or failure order. Label communication, storage ownership, and trust boundaries.]

## Critical journey and failure behavior

[Successful flow; acceptance versus completion; timeout/duplicate/partial failure behavior; recovery owner.]

## Alternatives

| Option | Hard constraints | Benefits for scenarios | Costs and risks | Evidence/confidence | Disposition |
|---|---|---|---|---|---|
| [Baseline] | [Pass/fail/unknown] | [Mechanism] | [Consequence] | [Source/assumption] | [Keep/reject/provisional] |

## Security and operations

[Authorization boundaries, sensitive data, deployment ownership, observability, recovery and operating cost assumptions relevant to this system.]

## Delivery and decision records

[Link ADRs and implementation slices. Specify compatibility, migration, cutover, and rollback limits where relevant.]

## Validation, risks, and revisit triggers

| Risk or uncertainty | Impact | Owner | Mitigation or experiment | Trigger for revisiting |
|---|---|---|---|---|
| [Risk] | [Consequence] | [Role] | [Check and acceptance criterion] | [Observable event] |

[Distinguish checks executed from checks proposed, and report remaining limits.]
