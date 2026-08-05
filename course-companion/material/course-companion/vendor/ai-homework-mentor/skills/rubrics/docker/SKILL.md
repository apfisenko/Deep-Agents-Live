---
name: rubric-docker
description: Review criteria for Docker and Docker Compose homework
---

# Rubric — Docker

## When to use

Student submission includes Dockerfile, docker-compose, or containerized app.

## Aspects

### dockerfile — Dockerfile

- Multi-stage or minimal image where appropriate
- Non-root user, healthcheck if applicable

### compose — Docker Compose

- Services defined clearly
- Environment variables, not secrets in image

### code-quality — Supporting code

- App starts correctly in container context

## Review procedure

1. Read the aspect brief and relevant files under `/code/`.
2. Check each criterion for the assigned aspect only.
3. Write findings to `/notes/<aspect-id>.md` with file paths.
4. Return a 3–5 line summary to the orchestrator.
