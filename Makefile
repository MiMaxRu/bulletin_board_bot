.PHONY: run-dev run-prod run-test build

run-dev:
	docker compose -f docker-compose.dev.yml up --build

run-prod:
	docker compose -f docker-compose.yml up --build -d

run-test:
	docker compose -f docker-compose.test.yml run --rm web pytest -q

build:
	docker build -t bulletin-board-bot:latest .
