# Architecture review playbook

Use this original workflow to produce findings supported by evidence. Adjust scope to the request; do not turn every review into a system rewrite.

## Establish scope and evidence

Record the repository revision or proposal version, business goal, constraints, inspected paths, commands executed, and inaccessible areas. Read project instructions and existing decisions. Follow the primary user journey and one important failure path through actual symbols and configuration.

Separate evidence classes:

| Class | Meaning | Appropriate language |
|---|---|---|
| Observed | Visible in code, configuration, trace, or executed check | The handler writes the record before publishing; cite the actual symbol |
| Requirement | Supplied by the user or accepted project document | The design must preserve this invariant |
| Inferred risk | Plausible consequence not yet reproduced | This sequence may lose work if publication fails; state the conditions |
| Unknown | Missing access, measurement, or decision | Capacity under the target workload is unverified |

Do not cite a file you have not inspected. Do not call a concern a reproduced bug without a reproduction. Absence from a limited search is not proof that a control does not exist anywhere.

## Inspect the seams

- **Responsibilities:** find unclear ownership, duplicated policy, dependency cycles, and cross-module mutations.
- **Contracts:** check inputs, errors, compatibility, cancellation, deadlines, and synchronous/asynchronous expectations.
- **Data:** trace authoritative writes, transaction scopes, invariants, tenancy, caches, and migrations.
- **Failure:** examine retries, unknown outcomes, duplicates, recovery, and backlog growth.
- **Operations:** identify deployment coupling, observability, incident ownership, restore procedures, and irreversible changes.
- **Security:** check trust boundaries, authorization, credentials, and data exposure on relevant paths.
- **Changeability:** use a plausible upcoming change to assess whether the abstraction helps.

Map each issue to a consequence for the user's goal. Avoid comments based only on naming, folder aesthetics, or a preferred architecture style.

## Write actionable findings

Each finding contains:

1. A concrete title and impact level.
2. Evidence: actual path and symbol, proposal section, or observed result.
3. Trigger and consequence.
4. The smallest adequate correction, with its tradeoff.
5. Verification or the next discriminating measurement.

Use impact levels consistently:

| Level | Use for |
|---|---|
| Critical | A credible path to severe harm such as broad unauthorized access or irreversible loss; explain reachability and evidence |
| High | A likely important correctness, availability, or integrity failure under expected conditions |
| Medium | A bounded reliability, maintainability, or efficiency issue with a clear consequence |
| Low | A limited concern that still has a concrete benefit to fix |

Reserve severity for supported impact, not how strongly you prefer a pattern. Keep open questions separate from findings. If no material issue is found, say what was inspected and which risks remain untested.

## Review a proposal before building

Check that the preferred design satisfies hard constraints, identifies ownership, survives important failures, and has a workable first slice. Ask which requirement each major component serves. Challenge extra infrastructure and missing infrastructure equally.

Check whether the document describes logical boundaries, deployment units, and security boundaries distinctly. Require an explanation for shared data ownership, coordinated service releases, and irreversible migrations.

## Validate proportionately

Choose checks that could disprove a finding or validate a material requirement. Examples: a contract test, a migration rehearsal with old and new versions, a duplicate-delivery test, a dependency-boundary check, or a representative load measurement.

Do not add tests that merely restate template fields or implementation details. Do not run destructive workloads against production without authorization. Stop once the concrete risk is sufficiently resolved and report remaining limits.

## Hand off a bounded plan

Order work by risk and dependency. Give each slice an outcome, scope, acceptance criterion, test or observation, and rollback/containment where relevant. Keep unrelated refactoring out of a focused fix.

For independent reviewers, provide the requirements and raw proposal/code. Avoid leaking a preferred verdict. Treat disagreement as a prompt to inspect evidence, not to average opinions.
