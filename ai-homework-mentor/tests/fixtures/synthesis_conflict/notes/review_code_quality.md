"""Code quality note — conflicts with architecture on CLI separation."""

# Aspect: code_quality

## Findings

- Entrypoint mixes argument parsing with business logic — no real separation.
- Public functions lack type hints.

## Risks

- Harder to test the core logic in isolation.
