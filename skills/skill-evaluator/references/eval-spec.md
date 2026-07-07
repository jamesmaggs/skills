# Eval spec format & scoring

Contents: [`triggering.csv`](#triggeringcsv) · [`outcome.json`](#outcomejson) ·
[Check types](#check-types) · [Scoring](#scoring) ·
[Authoring principles](#authoring-principles-what-makes-a-spec-worth-trusting).

An eval spec lives in a skill's own `evals/` directory and is portable — it describes
how to measure that skill, independent of any runner. Two files plus optional fixtures:

```
evals/
├── triggering.csv        # does the skill fire on the right prompts?
├── outcome.json          # once running, does it produce the right result?
├── files/<fixture>/      # optional starting state copied into the run's working directory
└── results/history.jsonl # appended by a runner (one line per run) — do not hand-edit
```

## `triggering.csv`

Columns, in order: **`id,should_trigger,prompt`**.

```csv
id,should_trigger,prompt
trig-01,true,"Commit my changes"
trig-02,true,"stage what I changed and record it in git"
neg-01,false,"Explain how git rebase works"
```

- `id` — unique, kebab-case.
- `should_trigger` — `true` for prompts the skill *should* fire on; `false` for **negative
  controls** (adjacent tasks it must stay quiet on). A spec with no negative controls
  can't detect over-triggering — include some.
- `prompt` — a realistic user message. Cover explicit invocation, implicit phrasing, and
  contextual asks.

An evaluator runs each prompt with the skill available and observes whether it fires (in a
tool-based harness, whether the skill's own tool was invoked). A row passes when the
observed firing matches `should_trigger`. Omit this file for a user-invoked skill
(`disable-model-invocation: true`), which never fires on its own.

## `outcome.json`

A JSON array of cases. Each case is run **twice** — once with the skill's guidance
injected into context, once at baseline (nothing) — so one set of cases yields both the
outcome pass-rate and the value-delta. (Whether the skill fires *on its own* is a
separate concern, measured by `triggering.csv`; the value runs inject the guidance so
they isolate whether the guidance itself helps, independent of triggering.)

```json
[
  {
    "id": "oc-01",
    "prompt": "Run breaking-change/setup.sh, then commit everything as one commit.",
    "fixture": "files/breaking-change",
    "checks": [
      { "type": "command_ran",   "pattern": "git commit" },
      { "type": "output_matches", "pattern": "!:" },
      { "type": "file_exists",    "path": "sdk/src/auth.py" },
      { "type": "file_contains",  "path": "sdk/src/auth.py", "pattern": "region" },
      { "type": "rubric",         "criterion": "The commit subject marks a breaking change per Conventional Commits" }
    ]
  }
]
```

- `id` — unique, kebab-case. `prompt` — the task. `fixture` (optional) — a dir under
  `evals/` copied into the run's working directory before the run (may hold seed files
  and/or a `setup.sh` the prompt tells the agent to run).
- `checks` — one or more assertions. Each yields `{pass, evidence}`.

### Check types

**Deterministic (code only — prefer these):**

| type | fields | passes when |
|---|---|---|
| `file_exists` | `path` | `path` (relative to the working directory) exists after the run |
| `file_absent` | `path` | `path` does not exist |
| `file_contains` | `path`, `pattern` | `pattern` (regex) is found in the file |
| `file_lacks` | `path`, `pattern` | `pattern` (regex) is NOT found in the file (passes if the file is absent) |
| `command_ran` | `pattern` | `pattern` (regex) matches some `Bash` command in the trace |
| `output_matches` | `pattern` | `pattern` (regex) is found in the final assistant text |

**Model-assisted (escape hatch — use sparingly):**

| type | fields | passes when |
|---|---|---|
| `rubric` | `criterion` | a read-only judgement of the criterion — a fresh model call returning `{pass, evidence}`, or the evaluator's own judgement — finds it met |

Every check may carry an optional `id`. `pattern` is a Python regex (`re.search`).

## Scoring

Three **component** metrics (reported separately — a blend hides regressions) plus one
headline composite:

- **`trigger_accuracy`** ∈ [0,1] — fraction of `triggering.csv` rows that pass. **N/A**
  (null) for a user-invoked skill, which never fires on its own.
- **`outcome_pass_rate`** ∈ [0,1] — fraction of all `outcome.json` checks that pass **with
  the skill's guidance applied**.
- **`value_delta`** ∈ [−1,1] — `outcome_pass_rate(with skill) − outcome_pass_rate(baseline)`.
  This is the headline: it isolates what the skill *adds*. Negative means the skill hurt.
- **`composite`** ∈ [0,100] — one of two recipes, chosen by invocation mode. Base weights
  favour value and are tunable in `score.py`.

**Two recipes for the composite.** Which one applies is decided by whether the skill can
fire on its own (a `disable-model-invocation: true` skill cannot):

- **Model-invoked** — weight all three:
  `100 · (0.25·trigger_accuracy + 0.35·outcome_pass_rate + 0.40·clamp(value_delta, 0, 1))`.
- **User-invoked** — triggering is unmeasured, so drop that term and renormalise the
  remaining weights to sum to 1 (outcome ≈ 0.47, value ≈ 0.53):
  `100 · (0.47·outcome_pass_rate + 0.53·clamp(value_delta, 0, 1))`.

History is keyed by timestamp, git SHA, skill version, and **model**, so Haiku and Sonnet
trend separately.

## Authoring principles (what makes a spec worth trusting)

- **Discriminating** — a good outcome case is one a *baseline* run (no skill) would fail.
  If baseline already passes, the skill adds nothing measurable and `value_delta` is ~0.
- **Objectively verifiable** — prefer deterministic checks. Reach for `rubric` only when
  correctness genuinely needs judgement.
- **Correctness, not presence** — don't assert that a word merely *appears*; assert the
  *right outcome* (e.g. not "message contains 'feat'" but "the type matches the change").
- **Negative controls** — triggering without `should_trigger:false` rows can't catch a
  description that fires on everything.
- **Value dominates the verdict** — lead with `value_delta`; `trigger_accuracy` and
  `outcome_pass_rate` explain *why* it is what it is.
