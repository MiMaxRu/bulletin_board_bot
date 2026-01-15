# Bulletin Board Bot (aiogram)

Production-ready async bulletin-board service with two Telegram bots (client + admin).

Quick start (dev):

1. Copy .env.example to .env.dev and fill in tokens and DB settings.
2. Run: make run-dev

Folder layout (initial):
- app/
  - bots/
    - client_bot.py
    - admin_bot.py
  - core/
    - config.py
    - logging.py
  - db/
    - session.py
    - models.py
  - main.py
- alembic/
- tests/
- Dockerfile
- docker-compose.yml
- docker-compose.dev.yml
- Makefile

Security: do NOT commit real tokens. Use .env files (gitignored).
