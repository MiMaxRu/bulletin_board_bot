# Running

Dev: `make run-dev` (uses docker-compose.dev.yml). The entrypoint runs migrations on start.

Production: `make run-prod` (ensure `.env.prod` set, webhook settings configured if `USE_WEBHOOK=true`).

To manually run migrations: `make migrate` or `alembic upgrade head`.
