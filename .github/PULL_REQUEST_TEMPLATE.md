### What this PR does

- Feature: registration for users and FSM-based ad creation (client bot)
- DB: repository for users/ads, Alembic initial migration
- Tests: unit tests for repository

### Checklist
- [x] Code follows project structure
- [x] Tests added/updated
- [x] Alembic migration included
- [ ] CI passes (ruff, mypy, pytest)

### How to test
1. Run dev stack: `make run-dev`
2. Use client bot `/register` and `/create` to create an ad
3. Run tests: `pytest`

### Notes
- Tokens must be set in `.env.dev` locally (not committed)
- Next: admin notifications + moderation flow
