# Development Workflow

## Approach

Build this project incrementally using a spec-driven workflow. Context files define what to build, how to build it, and what the current state of progress is. Always implement against these specs — do not infer or invent behavior from scratch.

## Scoping Rules

- Work on one feature module at a time.
- Prefer small, verifiable increments over large speculative changes.
- Do not combine unrelated system boundaries in a single implementation step.
- A "feature module" is one entry under `features/` — e.g. `cows`, `milk`, `predictions`.

## When To Split Work

Split an implementation step if it combines:

- Model changes and serializer/view changes in the same step
- API route logic and Celery task logic
- Multiple unrelated feature modules
- ML service calls and Django business logic in the same handler
- Behavior that is not clearly defined in the context files

If a change cannot be verified end to end with a single `pytest` run or a single curl, the scope is too broad — split it.

## Handling Missing Requirements

- Do not invent endpoint behavior that is not defined in the context files.
- If a requirement is ambiguous, resolve it in `architecture-context.md` before implementing.
- If a requirement is missing entirely, add it as an open question in `progress-tracker.md` before continuing.

## Protected Foundation Components

Do not modify the following unless explicitly instructed:

- `shared/renderers.py` — standard response wrapper
- `shared/pagination.py` — pagination classes
- `shared/middleware.py` — request logging
- `shared/permissions.py` — role permission classes
- `shared/exceptions.py` — custom exception classes and handler
- Any migration file that has already been applied

Project-specific logic must live in the relevant `features/<module>/` directory — not in shared infrastructure.

Only modify shared files when a task explicitly requires it and when the change is backward-compatible across all modules.

## Keeping Docs In Sync

Update the relevant context file whenever implementation changes:

- System architecture or module boundaries → `architecture-context.md`
- New or changed API endpoint → `api-context.md`
- Code conventions or patterns → `code-standards.md`
- Feature progress or decisions → `progress-tracker.md`

Progress state must reflect the actual state of the implementation, not the intended state. Never mark a feature complete until its tests pass and the endpoint is reachable.

## Before Moving To The Next Module

1. The current module's endpoints return correct responses for valid and invalid input.
2. All custom exceptions return the correct `error_code` and HTTP status.
3. No invariant defined in `architecture-context.md` was violated.
4. `progress-tracker.md` is updated to reflect exactly what was implemented, what files were changed, and any decisions made.
5. Any new endpoint is documented in `api-context.md`.
