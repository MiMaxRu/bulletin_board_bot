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

---

## Быстрый старт (dev) ✅

1. Скопируйте пример переменных окружения и заполните значения:

```bash
cp .env.example .env.dev
# или вручную создайте .env.dev
```

2. Запустите окружение в Docker:

```bash
docker compose -f docker-compose.dev.yml up --build -d
```

3. Проверка:
- Логи бота: `docker compose -f docker-compose.dev.yml logs -f bot`
- Выполните `get_me` внутри контейнера или отправьте сообщение своему боту в Telegram.

---

## Миграции Alembic 🔧

- Применить миграции локально/в контейнере:

```bash
alembic upgrade head
```

- Команды для разработки есть в `Makefile` (см. `make help`).

---

## Тесты и CI 🧪

- Локально запустить тесты с покрытием:

```bash
pytest --cov=app --cov-report=term-missing -q
```

- В репозитории настроен Github Actions для запуска `ruff`, `mypy` и `pytest` с проверкой покрытия (80%).

---

## Вклад и PRs 🤝

- Создавайте небольшие логические PR (feature/tests/docs).
- В PR добавьте описание, список проверок (миграции/тесты/линтер).

---

Если нужно — могу автоматически подготовить PR с этими изменениями (пока локально закоммичу изменения и создам ветку).
