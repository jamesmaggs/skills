# Deploy-target defaults

Starting points, not mandates. The skill is tool-agnostic: adopt whatever the confirmed stack and
target already imply, and prefer tools the team knows. Use this only to avoid dithering — every
choice stays reviewable in the plan. Whatever the target, three things always hold: **provision as
IaC**, **deploy from CI**, and **run the end-to-end test against the deployed system**.

## Contents

- [Choosing an e2e harness](#choosing-an-e2e-harness)
- [CI runners](#ci-runners)
- [IaC tooling](#iac-tooling)
- [Deploy targets](#deploy-targets)
- [Secrets](#secrets)

## Choosing an e2e harness

Match the harness to how the deployed system is actually reached:

- **Browser UI** — Playwright (preferred; cross-browser, good CI story) or Cypress.
- **HTTP/JSON API** — the stack's native test runner driving a real HTTP client against the
  deployed URL (e.g. `pytest` + `httpx`, `supertest`/`vitest`, Go `net/http` tests).
- **CLI / service** — a shell or native test that invokes the built binary against the deployed
  backend.
- **gRPC** — the language's gRPC client in the native test runner.

The harness must hit the **deployed** endpoint (a URL/host), configurable per environment — never
an in-process instance.

## CI runners

- **Code on GitHub →** GitHub Actions.
- **Code on GitLab →** GitLab CI.
- Otherwise match the host (Bitbucket Pipelines, Azure Pipelines, CircleCI).

The pipeline runs, in order: build → provision/apply IaC → deploy → e2e test against the deployed
system.

## IaC tooling

- **General / multi-cloud →** Terraform or OpenTofu.
- **Already in a language ecosystem →** Pulumi or CDK (AWS) can keep infra in the app's language.
- **Kubernetes target →** Helm charts or plain manifests under version control.
- **PaaS with a declarative manifest →** its own config file *is* the IaC (see below); commit it.

Never provision by clicking a console. If the target only supports console setup, capture the
result as import blocks or a documented, version-controlled script.

## Deploy targets

- **PaaS (Railway, Fly.io, Render, Vercel, Netlify)** — declarative manifest (`railway.json`,
  `fly.toml`, `vercel.json`, etc.) committed; deploy via the platform CLI from CI. Fastest path to
  a production-like URL.
- **Containers on a managed platform (Cloud Run, ECS/Fargate, App Runner, Azure Container Apps)** —
  `Dockerfile` + Terraform/Pulumi for the service and its networking; push image and deploy from CI.
- **Kubernetes** — image build + Helm/manifests applied from CI to a real (production-like)
  cluster.
- **Serverless (Lambda, Cloud Functions)** — SAM/Serverless Framework/Terraform; deploy from CI.
- **VM / on-prem** — Terraform (or equivalent) for the machine, a configuration step
  (cloud-init/Ansible), deploy from CI over SSH. Heaviest; only when a constraint demands it.

For a first skeleton, prefer the lightest target that is still genuinely production-*like* for this
project's constraints.

## Secrets

The agent never handles secret values. The user authenticates (`! <login command>`) and places
secrets into the platform's own store:

- **GitHub Actions →** repository/environment secrets.
- **Cloud →** the provider's secret manager (AWS Secrets Manager/SSM, GCP Secret Manager, etc.).
- **PaaS →** the platform's environment-variable/secret UI or `secrets set` CLI, run by the user.

IaC and CI reference secrets **by name**; a value never appears in the repo, the chat, or the plan
file.
