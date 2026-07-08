# 0001. Use REST for the public API

- Status: Accepted
- Date: 2024-01-15

## Context and drivers

We need a public API for third-party integrators, and the team is most familiar
with HTTP verbs and status codes.

## Considered options

- REST over HTTP
- GraphQL

## Decision

Use REST over HTTP for its simplicity and cacheability.

## Consequences

Integrators use standard HTTP verbs and benefit from HTTP caching, but cannot
fetch nested resources in a single request.
