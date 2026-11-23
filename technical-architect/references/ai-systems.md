# Architecture for AI applications and agents

Use this optional original extension when the system includes models, retrieval, generation, or autonomous tools. It is not extracted from either Head First book. Verify model/provider details against current primary documentation.

## Separate policy, model behavior, and side effects

Place deterministic authorization, budgets, validation, and irreversible-effect controls outside model discretion. Give each tool a narrow contract, scoped identity, validated arguments, result schema, timeout, and auditable operation ID.

Treat retrieved documents, tool output, websites, and model output as untrusted data. A document's instructions must not grant permissions or override the user's task. Enforce resource and tenant authorization before retrieval and again at the effect boundary where appropriate.

Use a workflow or state machine when the steps and invariants are known. Justify an open-ended agent loop with a concrete need for adaptive planning. Bound iterations, wall time, token/spend budget, concurrency, and retries.

## Choose a model boundary using evidence

Record the task distribution, quality threshold, latency target, context needs, privacy constraints, cost per successful outcome, hardware limits, and fallback behavior. Compare a deterministic baseline, a smaller model, and a stronger model only when they are credible candidates.

Evaluate on representative held-out cases and difficult slices. Keep prompts and evaluation data separate when measuring generalization. Report sample size, uncertainty, failure categories, and changes to the prompt/model/data. A favorable average may hide unacceptable failures in a critical slice.

Separate quality evaluation from observability. A trace shows what happened; an evaluation judges whether the outcome met the goal. Use human review or independent checks when the metric is an unreliable proxy. Do not claim a perfect judge or treat agreement between correlated models as ground truth.

## Own data and memory

Distinguish source documents, derived embeddings, user facts, transient conversation state, agent plans, and authoritative business records. Define provenance, access, retention, correction, deletion, and reindexing behavior for each.

For retrieval, specify query construction, authorization filters, freshness, deduplication, grounding/citations, and what happens when retrieval is empty or contradictory. Test deletion propagation and cross-tenant isolation. Do not assume embeddings replace access control or that retrieved text is correct.

For long-running agents, persist explicit task state, leases or ownership, progress, operation identities, and recovery decisions. Do not use conversation text alone as the durable source of truth for completed side effects.

## Design observable failure behavior

| Risk | Required design question |
|---|---|
| Invalid or unsupported output | How is it validated, rejected, repaired, or escalated without a harmful effect? |
| Provider timeout after tool execution | How is the same operation reconciled without duplicating the effect? |
| Excess cost or looping | Which deterministic budget stops further work, and what state is retained? |
| Model or prompt change | Which evaluation and rollback criteria must be satisfied? |
| Retrieval leakage | Where is authorization enforced and verified? |
| Low confidence or conflicting evidence | How does the workflow abstain, ask, or hand off? |
| Human approval needed | What concrete artifact is presented, and how is approval bound to that exact action? |

Keep safety and quality requirements concrete to the application. For a low-impact draft, ordinary review may suffice. For external messages, purchases, or privileged changes, preserve the user's authorization boundaries and bind execution to reviewed intent.

## Deliver the plan

Specify the model contract, deterministic controls, data ownership, evaluation gate, failure policy, cost assumptions, and first vertical slice. Mark hardware and provider capacity as estimates until measured. Explain which quality or workload change would justify a different model or architecture.
