# Bulletin Board Bot (skeleton)

Проект: Асинхронный сервис доски объявлений с ботами (aiogram).

Цель этого PR — создать skeleton проекта, CI, Docker и запустить минимальный контейнер с healthcheck.

Основное:
- Python 3.11+
- aiogram 3.x
- SQLAlchemy async + asyncpg
- Alembic
- Docker Compose (dev/test/prod)
- loguru
- pytest + pytest-asyncio
- mypy (strict) + ruff
- MkDocs для документации

Запуск локально (dev):

1. Скопировать `.env.example` -> `.env` и заполнить переменные
2. make run-dev

Важно: не коммитить реальные токены/секреты — храните их в `.env` и в секретах CI.
