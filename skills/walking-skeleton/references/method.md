# The walking skeleton method

The load-bearing principles behind this skill, distilled from Freeman & Pryce's
*Growing Object-Oriented Software, Guided by Tests* (the "walking skeleton", after Cockburn).

## What it is

A walking skeleton is an implementation of the **thinnest possible slice of real functionality
that can be automatically built, deployed, and tested end-to-end**. It includes just enough of the
automation, the major components, and the communication between them to start work on the first
feature. Keep the application functionality so simple that it's obvious and uninteresting — the
attention belongs on the infrastructure, not the feature.

## Why it exists — the first-feature paradox

Building the tooling and the first feature at the same time is hard: changes in one disrupt the
other, and failures are tricky to trace when the architecture, tests, and production code are all
moving at once. A symptom of an unstable environment is that there's **no obvious first place to
look when something fails**. Split the paradox: first work out how to build, deploy, and test a
skeleton; *then* use that infrastructure to write the acceptance test for the first real feature.
After that, everything is in place for test-driven development of the rest of the system.

## "End-to-end" means the process, too

The "end" in end-to-end refers to the **process**, not just the system. The test should start from
scratch, build a deployable system, deploy it into a **production-like environment**, and run
through the deployed system. Including deployment in the tested loop matters for two reasons:

1. Deployment is error-prone and must not be done by hand — the scripts should be thoroughly
   exercised long before the real deploy.
2. This is where the team meets the rest of the organisation. If it takes six weeks and four
   signatures to provision a database, discover that now — not two weeks before delivery.

If true end-to-end testing is genuinely unreachable at first, stand up infrastructure that
implements the *current* understanding of the real system and environment — but treat that as a
stop-gap. Unknown risks remain until the tests really run end-to-end.

## Deciding the shape

Standing up the skeleton is the moment to make the **high-level** structural choices: the major
components needed for the first planned release and how they communicate. Rule of thumb: you should
be able to draw the design on a whiteboard in a few minutes. To choose sensibly you need a
high-level view of both functional and non-functional requirements.

## This is not Big Design Up Front

Do **not** elaborate the whole design down to classes and algorithms first. Make the *smallest
number of decisions* needed to kick-start the TDD cycle, so you can start learning from real
feedback. Early guesses are likely wrong; discover the details by growing the system.

## Expect it to be slow

Teams are routinely surprised how long a skeleton takes given how little it does — because this
step establishes a lot of infrastructure and forces many awkward questions to be asked and
answered. That's the point. The work is the questions, not the feature.
