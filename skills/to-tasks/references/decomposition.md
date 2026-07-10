# Decomposition rubric

Two jobs: decide whether a story's acceptance criteria are testable (the gate),
and cut a story into tasks that are each one agent session and independently
verifiable.

## The testability gate

An acceptance criterion is testable when an agent could, from the criterion alone,
write a check that passes only when the behaviour is present. Concretely:

- **Concrete precondition** — the Given names real state ("a user with a verified
  email"), not "a valid user".
- **Concrete action** — the When is a single, specific action.
- **Observable outcome** — the Then is something you can assert: a status code, a
  returned or stored value, a rendered element, an emitted event, a persisted
  record.
- **No weasel outcomes** — "works correctly", "is fast", "is secure", "handles
  errors gracefully" are not observable until turned into a measurable rule (e.g.
  "responds 400 with error code EMAIL_TAKEN", "p95 latency < 200ms").

The gate fails if any criterion has no observable outcome, or the story has no
acceptance criteria at all. Do not paper over a vague criterion by inventing an
outcome — halt and flag. The point of the gate is that an untestable criterion
produces unverifiable tasks, and an agent cannot tell an unverifiable task from a
finished one.

## Sizing a task: one agent session

A task is right-sized when an agent can carry it from start to a passing
verification in a single focused session:

- one coherent change with one clear check;
- small enough that its verification is obvious and fast;
- large enough to deliver a real, checkable step — not "add an import".

If a task cannot be verified without first doing another task, either fold them
together (they are really one step) or record the dependency (they are genuinely
sequential).

## Independent verifiability

Each task carries the check that proves it done, and that check should run without
waiting on a sibling task wherever possible. Favour **vertical slices** — a thin
cut through whatever layers the change touches, verifiable end to end — over
horizontal layers (a "write the schema" task, a "write the handler" task) that are
individually unverifiable and force a dependency chain.

## Dependencies

Independence is the default; a dependency is a cost you accept only when the work
is truly sequential (e.g. a migration must exist before code can read the new
column). When you accept one:

- record it on the dependent task as `Depends on: <ids>`;
- keep the chain shallow — a long dependency chain means the tasks are cut wrong;
- never encode an ordering as a hidden assumption in prose.

## When the first task is a spike

If part of the story cannot be sized because of a genuine unknown, the right first
task is a **spike**: a time-boxed investigation whose verification is a recorded
decision or a proof-of-concept, not shipped behaviour. Later tasks depend on the
spike's finding.
