---
name: walking-skeleton
description: Stands up a walking skeleton at the start of a project — the thinnest end-to-end slice that is automatically built, deployed to a production-like target, and tested through the deployment, so the build-deploy-test process is proven before the first real feature.
disable-model-invocation: true
---

# Walking Skeleton

Establish a **walking skeleton**: the thinnest possible slice of real functionality that is
automatically **built, deployed to a production-like target, and tested end-to-end through the
deployment**. The goal is to prove the *process* — build, IaC provisioning, deploy, and an
end-to-end test that runs against the deployed system — not to ship a valuable feature. Keep the
functionality obvious and uninteresting; all the effort goes into the infrastructure.

Read `references/method.md` before planning. Consult `references/deploy-targets.md` when choosing
tooling for a confirmed deploy target.

**Standing invariant (every step):** never read, echo, store, or commit a secret value. Secrets are
placed by the *user* into the platform's own secret store; config and IaC reference them by name
only. Nothing secret ever enters the repo, the chat, or `docs/WALKING-SKELETON.md`.

## Step 0: Resume check

If `docs/WALKING-SKELETON.md` already exists, this is a resume, not a fresh run. **Skip Steps 1–4.**
Read the checklist, summarise progress (done / next unchecked step), and ask: *resume, or start
over?* On "resume", continue from the first unchecked step. On "start over", confirm before
discarding the file, then proceed from Step 1.

## Step 1: Bail-gate

The skill only applies before a build→deploy→test pipeline exists. Sweep for signs one is already
present:

- **CI config** — `.github/workflows/`, `.gitlab-ci.yml`, `.circleci/`, `Jenkinsfile`, Azure
  Pipelines, etc.
- **Deploy / IaC config** — Terraform/OpenTofu, Pulumi, CloudFormation/CDK, Helm/k8s manifests,
  `Dockerfile` wired to a deploy, `vercel.json`, `railway.json`, `fly.toml`, `serverless.yml`.
- **An existing end-to-end test harness** — a suite that drives a deployed or running system.

Application code alone (source, a dependency manifest, unit tests) does **not** disqualify a
project — a missing pipeline is exactly what this skill adds.

- **Pipeline clearly present →** stop. Tell the user this isn't the right time for a walking
  skeleton and why, and end.
- **Signals mixed / ambiguous →** report exactly what was found and ask whether to proceed.
- **No pipeline →** continue.

## Step 2: Discover the stack

Infer a proposed stack from two sources:

- **Documentation** — `README`, `docs/`, PRDs, design notes: what the product is, its major
  components, any stated constraints.
- **Latent repo signals** — lockfiles, version pins (`.nvmrc`, `.tool-versions`, `go.mod`,
  `pyproject.toml`), editor/CI stubs, stray configs, the language of any existing files.

Assemble a **proposed stack**: language/framework, major components and how they communicate,
data store (if any), and the **deploy target**. The deploy target is load-bearing and is almost
never written down — treat it as unknown unless a signal proves otherwise.

## Step 3: Confirm and interview

Present the proposed stack to the user and **confirm the deploy target explicitly**, every time —
even when the language and framework are obvious.

Interview *only* to fill genuine gaps, and stay aggressively narrow. Cover only what's needed to
draw the skeleton on a whiteboard:

- the one **trivial end-to-end behaviour** to prove,
- the **major components** and how they communicate,
- the **deploy target**,
- any **blocking non-functional constraints** that shape structure now (on-prem, regulated data,
  a mandated cloud).

At most one orienting question about what the product is. **Refuse feature discovery** — if the
user drifts into features beyond the first trivial one, redirect: those come after the skeleton
walks.

## Step 4: Plan

Propose the **canonical thinnest slice** for the confirmed architecture and the **first failing
end-to-end test that targets the deployed system** (not a local process — deployment must sit
inside the tested loop from step one). Pick the most boring slice that still exercises every layer
(for web+API+DB: one page rendering one value fetched from the DB through the API). Let the user
iterate on the slice and the test before anything is built.

Structure the plan as **baby steps outward from the failing e2e test**, each individually runnable
and verifiable so a failure has an obvious first place to look:

1. The failing end-to-end test that drives the deployed system.
2. Build automation (one command produces a deployable artifact).
3. IaC for the production-like environment.
4. The major components, wired together, doing the trivial slice.
5. CI that runs build → deploy → the e2e test.
6. Deploy, so the test finally passes through the deployed system.

Present the plan for approval in **plan mode**. On approval, write it to `docs/WALKING-SKELETON.md`
as a checklist using the template below.

### `docs/WALKING-SKELETON.md` template

```markdown
# Walking Skeleton

**Trivial slice:** <one-sentence description of the boring end-to-end behaviour>
**Stack:** <language/framework · components · data store>
**Deploy target:** <confirmed target>

## Steps
- [ ] Failing end-to-end test driving the deployed system
- [ ] Build automation (one command → deployable artifact)
- [ ] IaC for the production-like environment
- [ ] Components wired to perform the trivial slice
- [ ] CI: build → deploy → e2e test
- [ ] Deploy — e2e test passes through the deployed system

## Auth hand-offs
- [ ] <credential/login the user must perform, referenced by name>

## Notes
<decisions, blockers, links>
```

## Step 5: Execute

Work the checklist top to bottom, ticking each box in `docs/WALKING-SKELETON.md` as it lands.
Provision all infrastructure as **IaC** — reviewable, reproducible, part of the same pipeline —
never clicked together by hand. Prefer tooling the confirmed stack and target imply; use
`references/deploy-targets.md` for sane defaults.

**At every step that needs a credential or login:** stop. Give the user the exact command to run
themselves (suggest `! <command>`, e.g. `! gcloud auth login`), and wait. The agent provisions
infra; the *user* authenticates and places secret values into the platform's store. Reference
secrets by name in IaC and CI; never materialise a value. Record the hand-off in the plan file's
"Auth hand-offs" section.

## Step 6: Deploy gate

Before the first real deploy — even though it rides the tail of the CI run — stop and ask the user
explicitly: *ready to take the plunge and deploy?* Deploy only on a clear yes.

## Step 7: Done

Done when the end-to-end test passes **through the deployed system** and the user confirms the
skeleton walks. Then offer to delete `docs/WALKING-SKELETON.md` — it was a temporary map, not a
lasting artifact.
