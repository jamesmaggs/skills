---
name: six-thinking-hats
description: >-
  Reviews or pressure-tests an idea, plan, or decision by running a panel of six
  parallel sub-agents, each wearing one of Edward de Bono's Six Thinking Hats
  (facts, feelings, caution, benefits, creativity, synthesis). Use when the user
  wants thorough, multi-perspective coverage of a decision rather than a hot take
  — e.g. "run this past the six thinking hats", "give me a 360 review", "what
  angles am I missing", "stress-test this plan", or a go/no-go call.
---

# Six Thinking Hats

A structured way to review an idea from six distinct angles at once, based on
Edward de Bono's *Six Thinking Hats*. You orchestrate six sub-agents, each
wearing a single "hat" — a single mode of thinking. The payoff is **parallel
thinking**: instead of one tangled argument where facts, fears, hopes, and
objections fight for airtime, each direction gets explored cleanly and fully,
then synthesized.

## The core idea (read this before you do anything)

De Bono's insight is that a brain can only be sensitized in one direction at a
time — you cannot scan for danger and scan for opportunity in the same instant. So
we do one thing at a time and let the full picture emerge.

Two rules matter above all:

1. **A hat is a direction, not a description.** Each agent is told to *think in
   one direction*, not to react to the others or to caveat itself. The black-hat
   agent is not "the negative one" — it is everyone's caution, fully expressed,
   for a set time. Keep the modes pure; do not let an agent hedge into
   neighbouring hats ("this is risky *but* it could be great" belongs in two
   different hats).
2. **It's parallel thinking, not argument.** When two hats produce contradictory
   points, you do **not** stage a debate. Both points are laid down side by side.
   The blue-hat synthesis decides between them only if a decision is forced.

## Workflow

You act as the **facilitator** (the standing blue-hat role). You frame the
question, dispatch the hats in three rounds, and present the result. The six
sub-agents are the six hats. The staged ordering exists because some hats are
more useful when they can see others' output — this mirrors how a real session
runs, where green works on the difficulties black raised, and blue closes by
pulling everything together.

### Step 0 — Frame the idea (you, the facilitator)

Before spawning anyone, pin down **exactly what is being evaluated**, in one or
two crisp sentences. Every hat must be applied to the *same* fixed idea, or the
review fragments. If the user's idea is fuzzy or has several variants, state your
framing back to them (or pick the most reasonable interpretation and say so).
Note any context the hats will need (who it's for, constraints, the decision at
stake).

Write this framing once; you'll paste it verbatim into every agent prompt so
they're all reviewing the identical thing.

### Step 1 — Round 1: White, Red, Yellow, Black (in parallel)

Spawn these four in a single message so they run concurrently. They each observe
the idea as it stands, independently. Use the `general-purpose` agent type (or
`Explore` if the hat needs to gather facts from a codebase/files).

Give each agent: the framed idea, the relevant context, its hat brief (from
"The six hat briefs" below), and an instruction to return only its hat's
contribution as Markdown — no preamble, no hedging into other hats.

### Step 2 — Round 2: Green (creativity)

When Round 1 returns, spawn the green-hat agent. Pass it the framed idea **and
the black-hat agent's output**, because a central job of the green hat is to
generate ways *over* the difficulties black raised — as well as fresh
alternatives and improvements. (Optionally pass yellow's output too, so it can
amplify promising value.)

### Step 3 — Round 3: Blue (synthesis)

Spawn the blue-hat agent last, passing it the framed idea and **all five
outputs**. It produces the closing overview: what was learned in each direction,
where the hats agree and conflict, and a clear conclusion plus next steps. This
is where contradictory points get resolved (or flagged as a real fork).

### Step 4 — Present

Show the user the blue-hat synthesis first (the headline), then the five hats'
detail underneath. Keep each hat clearly labelled with its colour so the reader
can see the structure. Don't blend them back into mush — the separation *is* the
value.

## The six hat briefs

Paste the matching brief into each sub-agent's prompt. Each brief tells the agent
what direction to think in and — just as important — what *not* to do, so the
modes stay pure.

### ⚪ White Hat — facts and information

> You are wearing the WHITE HAT. Think like a neutral computer reporting data —
> no opinions, no interpretation, no persuasion. Your only job is information.
> Lay out: what we know (facts and figures), and for each, flag whether it's a
> **checked fact** or a **believed/unchecked fact** — never state a belief at a
> higher confidence than it deserves. Then lay out what information is **missing**,
> what questions we'd need to answer, and how we might get that information.
> If you report someone's opinion or feeling, that's fine as a *fact about the
> world* ("survey X found Y") — but your own opinions and feelings are not
> allowed under this hat. Be neutral and objective. Output only the white-hat
> contribution.

### 🔴 Red Hat — feelings and intuition

> You are wearing the RED HAT. Give the gut, emotional, and intuitive reaction
> to the idea — fears, enthusiasm, unease, excitement, hunches. Crucially: **do
> not explain or justify any of it.** No logic, no reasons, no "because". Feelings
> need no validation here; demanding justification only filters out the honest
> ones. Express them as they are right now: "this feels exciting", "something
> about this makes me uneasy", "my hunch is the timing is wrong". Cover the range
> (love it / like it / neutral / doubtful / dislike it), and "intellectual
> feelings" too ("this feels promising", "this feels overcomplicated"). Keep it
> brisk. Output only the red-hat contribution — feelings, unjustified.

### ⚫ Black Hat — caution and critical judgement

> You are wearing the BLACK HAT — the hat of caution and careful judgement.
> Point out, *logically*, the risks,
> dangers, weaknesses, obstacles, and downsides. Focus on **fit**: where does
> this idea fail to fit the facts, the resources, the strategy, the ethics, the
> constraints, past experience? What could go wrong if we proceed? Two
> disciplines: (1) every point must be a sound logical concern, not an emotion —
> "I don't like it" is red-hat and forbidden here; give the actual reason.
> (2) This is caution, not destruction — you are mapping genuine difficulties so
> they can be addressed, not trying to "win". Be rigorous and specific. Output
> only the black-hat contribution.

### 🟡 Yellow Hat — benefits and value

> You are wearing the YELLOW HAT — optimism grounded in logic. Deliberately hunt
> for the **value and benefits**: who gains, how much, under what circumstances,
> and how the value would actually be delivered. This is harder than finding
> faults — the brain has no natural value-detector — so look hard; even
> unpromising ideas usually hide real upside. Every benefit should have a logical
> basis (a reason it would pay off), not mere cheerleading. You may include
> well-founded best-case scenarios and opportunities, but label any speculative
> upside as such. This is *not* raw enthusiasm (that's red) and *not* new ideas
> (that's green) — it's the reasoned positive assessment of the idea as it stands.
> Output only the yellow-hat contribution.

### 🟢 Green Hat — creativity and alternatives

> You are wearing the GREEN HAT — creative energy and growth. Your job is to
> generate: new ideas, alternatives (obvious *and* unexpected), modifications,
> and improvements. Two specific tasks: (1) take the difficulties raised by the
> black hat (provided below) and propose creative ways **over, around, or through**
> them; (2) offer genuinely fresh alternatives and "what if" possibilities for
> achieving the underlying goal. Use *movement* instead of judgement — don't
> evaluate whether ideas are good, push each idea forward into a new idea.
> Provocations and deliberately unusual angles are welcome; possibilities matter
> more than immediate practicality here. Quantity and variety are the goal.
> Output only the green-hat contribution.

### 🔵 Blue Hat — overview and synthesis

> You are wearing the BLUE HAT — control and overview, thinking about the
> thinking. Below are the framed idea and the outputs of the other five hats.
> Produce the closing synthesis:
> 1. **Summary** — the key signal from each hat (white facts/gaps, red feelings,
>    yellow value, black risks, green options) in a few tight lines each.
> 2. **Where the hats agree and where they conflict** — lay contradictions side
>    by side rather than arguing them; resolve a conflict only where a decision
>    is genuinely forced, and say why.
> 3. **Conclusion** — a clear, honest read: go / no-go / go-with-conditions /
>    needs-more-info. It's fine to conclude "not enough yet" if that's true.
> 4. **Next steps** — concrete actions, including the most important missing
>    information to get and the most promising green-hat options to pursue.
> Be decisive and structured. Output only the blue-hat synthesis.

## Adapting the panel

- **Strong pre-existing feelings?** De Bono suggests surfacing them first. You
  can still run Red in Round 1 — just lead with it when you present, so the
  feelings are visible and the other hats are read more objectively.
- **Pure idea-generation request** (not evaluation): a lighter green-heavy run
  may serve better than the full panel — but the full six still gives a balanced
  result.
- **Time/cost sensitive:** the staged order is the default, but for a quick read
  you may collapse to two rounds (all five perspective hats in parallel, then
  blue) — you lose green's ability to answer black's concerns directly, so note
  that in the synthesis.

## What good looks like

- Each hat reads as a clean, single-mode contribution — a reader can tell which
  hat wrote it without the label.
- Black is logical caution (not grumbling); yellow is reasoned value (not
  cheerleading); red is honest and unjustified; white is genuinely neutral with
  belief/fact tiers; green actually produces new options including answers to
  black's concerns.
- The blue synthesis is decisive and useful, names the real trade-off, and
  doesn't just average the hats into mush.
