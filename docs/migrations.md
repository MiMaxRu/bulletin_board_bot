# Migrations

Alembic is configured. Typical commands:

- Create revision: `make alembic-revision` or `alembic revision --autogenerate -m "msg"`
- Apply migrations: `make migrate` or `alembic upgrade head`

Ensure `DATABASE_URL` is set in `.env.*`.
