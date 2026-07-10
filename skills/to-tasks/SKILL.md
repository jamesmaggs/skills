---
name: to-tasks
description: Decomposes a user story into small, independently verifiable tasks an agent can finish in a single session, records any dependencies between them, and writes them to the project's task tracker. Use when an agent picks up a story or issue to work on, or wants to break a story down into actionable tasks before implementing. First checks the story's acceptance criteria are testable and halts — flagging the story for clarification — if they are not.
---

# To Tasks

Pick up a story and turn it into the concrete tasks an agent will execute. Each
task is sized to **one agent session**: completable and independently verifiable
in a single pass, without needing another task's output first wherever possible.
Dependencies that genuinely exist are recorded, never hidden.

Before any of that, one **gate**: the story's acceptance criteria must be
*testable*. If they are not, you cannot verify the tasks you would derive from
them — so halt and send the story back for clarification rather than decomposing
guesswork.

## Step 1: Locate the trackers

Two destinations, resolved independently from the project's docs (`CLAUDE.md`,
`AGENTS.md`, `README`, `docs/`):

- **Story tracker** — where the story lives and where a clarification flag is
  written back. Usually GitHub Issues or a markdown backlog.
- **Task tracker** — where the tasks are written. Configured *separately* from the
  story tracker so the two can differ. Resolve it from the docs, or by detecting a
  tracker already in the repo: **Beads** (a local, dependency-aware tracker — a
  `.beads/` directory, or `bd` named in the docs), GitHub Issues, else a local
  markdown task store under `docs/tasks/`. Beads is the strongest fit for local
  agent task-tracking because it models dependencies natively and surfaces
  unblocked work (`bd ready`) — see Step 5.

Confirm tooling before use (`gh auth status` for GitHub; `bd version` for Beads).
State both resolved destinations in one line before continuing.

## Step 2: Select the story

If the caller names a story (issue number, id, or file), load that one. Otherwise
pick the next story that is not yet decomposed and not already flagged for
clarification — skip any story that already has tasks in the task tracker. State
which story you are decomposing.

## Step 3: Gate on testable acceptance criteria

Before decomposing, check **every** acceptance criterion is genuinely testable: a
concrete precondition, a concrete action, and an **observable** outcome you could
assert (a status code, a stored value, a rendered element, a logged event). A
criterion like "works correctly", "is fast", or "handles errors" is not testable;
a story with no acceptance criteria fails the gate outright. Read
`references/decomposition.md` for the full testability rubric.

If any criterion fails — **halt. Do not decompose.** Flag the story in its tracker
so the gap is visible where the story lives:

- **GitHub** — add a `needs-clarification` label (`gh label create
  needs-clarification --force`) and a comment naming each untestable criterion and
  what would make it testable.
- **Markdown** — append a clearly marked `> **Needs clarification:** …` note to the
  story file naming the same.

Then report the halt to the caller and stop. Do not invent an outcome to get a
vague criterion past the gate — that is exactly the guess the gate exists to catch.

## Step 4: Decompose into single-session tasks

Break the story into tasks where each one is:

- **single-session** — completable in one focused agent pass;
- **independently verifiable** — it carries its own check that proves it done,
  runnable without another task having run first wherever possible;
- **traceable** — it names the acceptance criterion or behaviour it advances.

Prefer independence: shape tasks so they don't need each other's output. Where a
task genuinely cannot start until another finishes, record the dependency
explicitly on the dependent task — never leave an ordering implicit (in Beads, as a
native `bd dep`; otherwise as the `Depends on:` line of the task shape below). If
most tasks depend on one another, they are cut wrong (horizontal layers); re-cut
into vertical slices so each stands alone. Read `references/decomposition.md` for
how to size a task, handle dependencies, and when a spike is the right first task.

## Step 5: Write the tasks

Write each task in this shape:

```
Task: <short imperative summary>

Story: <story ref / link>
Satisfies: <acceptance criterion or behaviour this advances>

## Verification
<the observable check that proves this task done — a test to run, a command and its
expected output, or a state to inspect — runnable in a single session>

## Depends on
<task ids, or "none">
```

- **Beads** — `bd init` first if `.beads/` is absent. Create each task with
  `bd create "<title>" -t task -d "<body>" --silent`, where the body carries Story,
  Satisfies, and Verification, and `--silent` returns the new stable `bd-…` id.
  Record dependencies natively rather than as a text line:
  `bd dep add <task-id> <prerequisite-id>` (default type `blocks`); log work
  uncovered mid-decomposition with `--deps discovered-from:<id>`. Read state with
  `--json` — `bd ready --json` then lists exactly the unblocked tasks an agent can
  pick up next, which is why getting the dependencies right here matters.
- **GitHub** — ensure a `task` label (`gh label create task --force`); create one
  issue per task, its body carrying Story, Satisfies, Verification, and Depends on,
  and cross-referencing the parent story.
- **Markdown** — write the tasks to `docs/tasks/<story-ref>.md` as a checklist, one
  entry per task in the shape above.

## Step 6: Report

List the tasks created (issue numbers/URLs or file path) and the dependency
ordering between them, and note the story as decomposed. If you halted at the gate,
report only the flagged criteria and where you recorded the flag.
