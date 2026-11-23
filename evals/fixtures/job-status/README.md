# Job status review fixture

This is an original synthetic fixture. It has no network access, production data, or external dependencies.

A single Python process serves job progress to authenticated users. `LiveStatusProvider` is the existing implementation. The proposed `CachedStatusProvider` should reduce expensive status reads while preserving the same public contract:

- Every call checks the current actor's access to the requested job. Access can be revoked between calls.
- Every successful read returns the latest committed status available at the time of the call.
- Job IDs are globally unique. Different actors may request the same job.

`ProgressFeed` is a proposed in-process notification mechanism. The caller supplies increasing revisions. Subscribers may synchronously commit a newer revision or remove themselves. Subscribers want the exact snapshot for each committed revision, in order; one subscriber's exception must not prevent the others from being notified. Process-crash recovery and durable messaging are outside this component's requirements.

Review the proposal before release. Keep the solution appropriate for one process. You may use local fakes to investigate, but do not modify the fixture or access live systems.
