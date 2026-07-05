# Sandbox image for running an untrusted skill under `claude -p --permission-mode
# bypassPermissions`. Everything the agent does happens inside this ephemeral
# container with only a throwaway /work dir mounted, so destructive tool calls
# cannot reach the host.
# Pinned by digest + version so the sandbox is reproducible (stable scores over
# time) and immune to a surprise upstream change. Bump deliberately.
FROM node:22-slim@sha256:813a7480f28fdadac1f7f5c824bcdad435b5bc1322a5968bbbdef8d058f9dff4

RUN apt-get update \
    && apt-get install -y --no-install-recommends git jq ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g @anthropic-ai/claude-code@2.1.201

# Run as the image's non-root `node` user (uid 1000). Claude refuses some
# bypass modes as root, and non-root keeps the blast radius smaller.
USER node
WORKDIR /work

# Args after the image name are passed straight to `claude`.
ENTRYPOINT ["claude"]
