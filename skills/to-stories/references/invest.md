# INVEST rubric

A story is ready to create only when it passes all six checks. For each letter:
what it asks, how to tell it is failing, and the move that fixes it. Prefer
fixing over dropping — a failing check usually means the story is shaped wrong,
not that the capability is unworthy.

## I — Independent

**Asks:** can this story be built and shipped without waiting on another story in
this batch?

**Failing when:** two stories touch the same new component and neither works
until both land, or a story's acceptance criteria reference behaviour defined
only in a sibling story.

**Fix:** decouple by carving the shared foundation into its own story and letting
the rest depend on it in sequence, or merge two truly inseparable slices into
one. Record any unavoidable ordering as a note, not a hidden assumption.

## N — Negotiable

**Asks:** does the story describe the outcome, leaving the implementation open?

**Failing when:** the story prescribes a specific class, library, or schema
instead of the behaviour the user needs — it reads like a task, not a story.

**Fix:** restate as capability and value (the "I want / so that"), and move any
genuine hard constraint into a `Rule:` line so it is explicit rather than baked
into the narrative.

## V — Valuable

**Asks:** does completing this deliver something a real role can perceive?

**Failing when:** the story delivers only internal plumbing ("add a repository
layer") with no user- or operator-visible result.

**Fix:** raise the altitude until there is a role who benefits, and name them in
the "As a" line. If the plumbing is genuinely necessary, fold it into the first
story that makes its value visible rather than shipping it naked.

## E — Estimable

**Asks:** is there enough clarity to gauge the effort?

**Failing when:** the team could not guess whether this is an hour or a month
because the spec is ambiguous or the unknowns dominate.

**Fix:** tighten the acceptance criteria with concrete pre/postconditions. If the
unknown is real, the right story may be a spike ("investigate X, produce a
recommendation") with its own testable outcome — the decision is recorded.

## S — Small

**Asks:** can this be finished in a single focused pass?

**Failing when:** the story spans multiple roles, several screens, or a long
Given/When/Then list that is really several features.

**Fix:** split into thin **vertical** slices — each slice still cuts through every
layer and delivers a usable sliver of the whole — never horizontal layers (UI
story, API story, DB story) that are individually worthless. One coherent
behaviour per story.

## T — Testable

**Asks:** can an agent verify it is done from the acceptance criteria alone?

**Failing when:** criteria say "works correctly", "is fast", or "handles errors"
without a concrete, observable outcome.

**Fix:** rewrite each criterion as a Given/When/Then with real inputs and an
outcome you can assert — a status code, a stored value, a rendered element, a
logged event. Turn quality bars into measurable rules (`Rule: p95 latency < 200ms`).
This is the check that makes a story agent-actionable, so hold it hardest.
