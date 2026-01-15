.PHONY: run-dev run-prod run-test build migrate alembic-revision

run-dev:
	docker compose -f docker-compose.dev.yml up --build

run-prod:
	docker compose -f docker-compose.yml up --build -d

run-test:
	docker compose -f docker-compose.test.yml run --rm tests

build:
	docker build -t bulletin_board_bot:latest .

migrate:
	alembic upgrade head

alembic-revision:
	alembic revision --autogenerate -m "add migration"
