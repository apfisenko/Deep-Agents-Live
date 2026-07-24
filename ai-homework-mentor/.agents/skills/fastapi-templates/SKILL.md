---
name: fastapi-templates
description: Create production-ready FastAPI projects with async patterns, dependency injection, and comprehensive error handling. Use when building new FastAPI applications or setting up backend API projects. Also use when reviewing student FastAPI homework for structure, DI, and async route patterns.
---

# FastAPI Project Templates

Production-ready FastAPI project structures with async patterns, dependency injection, middleware, and best practices for building high-performance APIs.

**Homework mentor note:** when reviewing student work, use this skill as a checklist of expected FastAPI structure — do not scaffold a new project and do not execute student code.

## When to Use This Skill

- Starting new FastAPI projects from scratch
- Implementing async REST APIs with Python
- Building high-performance web services and microservices
- Reviewing homework that includes FastAPI routes / API packages
- Setting up API projects with proper structure and testing

## Core Concepts

### 1. Project Structure

**Recommended Layout:**

```
app/
├── api/                    # API routes
│   ├── v1/
│   │   ├── endpoints/
│   │   └── router.py
│   └── dependencies.py
├── core/                   # Core configuration
├── models/                 # Database models
├── schemas/                # Pydantic schemas
├── services/               # Business logic
├── repositories/           # Data access
└── main.py                 # Application entry
```

### 2. Dependency Injection

FastAPI's built-in DI system using `Depends`:

- Database session management
- Authentication/authorization
- Shared business logic
- Configuration injection

### 3. Async Patterns

Proper async/await usage:

- Async route handlers
- Async database operations
- Async background tasks
- Async middleware

## Review checklist (mentor)

1. App entry creates `FastAPI()` and includes routers with a clear prefix.
2. Routes live under `api/` / `routes/` / `routers/`, not mixed into business logic.
3. Request/response use Pydantic schemas where appropriate.
4. Dependencies use `Depends` instead of globals where feasible.
5. Never execute the student app; never open `.env`.

## Source

Installed for AI Homework Mentor S5 from the trusted skills.sh catalog entry
`wshobson/agents` → `fastapi-templates` (verified description matches architecture review).
