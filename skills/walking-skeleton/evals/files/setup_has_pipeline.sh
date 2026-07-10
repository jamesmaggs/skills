#!/usr/bin/env bash
# Fixture: a project that ALREADY has a build->deploy->test pipeline.
# The walking-skeleton skill should bail here — this is past the skeleton stage.
set -euo pipefail

# Guard: only ever run in a throwaway directory. If we are inside a git work
# tree, this fixture would mutate the real repo (config, files) — refuse.
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Refusing to run inside a git repository — run this fixture in an empty temp directory." >&2
  exit 1
fi

git init -q
git config user.email fixture@example.com
git config user.name Fixture

mkdir -p src .github/workflows infra tests/e2e

cat > package.json <<'JSON'
{
  "name": "taskflow",
  "version": "0.1.0",
  "scripts": {
    "start": "node src/index.js",
    "test:e2e": "playwright test"
  }
}
JSON

cat > src/index.js <<'JS'
const http = require("http");
http.createServer((_, res) => res.end("ok")).listen(3000);
JS

cat > Dockerfile <<'DOCKER'
FROM node:20-slim
WORKDIR /app
COPY . .
RUN npm ci --omit=dev
CMD ["node", "src/index.js"]
DOCKER

cat > .github/workflows/deploy.yml <<'YML'
name: build-deploy-test
on: { push: { branches: [main] } }
jobs:
  ship:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t taskflow .
      - run: terraform -chdir=infra apply -auto-approve
      - run: npm run test:e2e
YML

cat > infra/main.tf <<'TF'
resource "google_cloud_run_service" "taskflow" {
  name     = "taskflow"
  location = "europe-west1"
}
TF

cat > tests/e2e/smoke.spec.js <<'JS'
const { test, expect } = require("@playwright/test");
test("home responds", async ({ page }) => {
  await page.goto(process.env.DEPLOY_URL);
  await expect(page.locator("body")).toContainText("ok");
});
JS

git add -A
git commit -qm "chore: taskflow service with CI, IaC, and e2e"
