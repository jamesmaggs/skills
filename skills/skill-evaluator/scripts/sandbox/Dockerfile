# Sandbox image for running an untrusted skill under `claude -p --permission-mode
# bypassPermissions`. Everything the agent does happens inside this ephemeral
# container with only a throwaway /work dir mounted, so destructive tool calls
# cannot reach the host.
FROM node:22-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends git jq ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g @anthropic-ai/claude-code

# Run as the image's non-root `node` user (uid 1000). Claude refuses some
# bypass modes as root, and non-root keeps the blast radius smaller.
USER node
WORKDIR /work

# Args after the image name are passed straight to `claude`.
ENTRYPOINT ["claude"]
