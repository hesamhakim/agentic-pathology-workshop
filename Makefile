.PHONY: help up down restart smoke test lint format reset clean

COMPOSE := docker compose -f .devcontainer/docker-compose.yml

help:
	@echo "Targets:"
	@echo "  up        Start langflow + phoenix + keybroker"
	@echo "  down      Stop all services"
	@echo "  restart   Down + up"
	@echo "  smoke     Run e2e smoke (requires services up)"
	@echo "  test      Run pytest"
	@echo "  lint      Run ruff"
	@echo "  format    Run ruff fix + black"
	@echo "  reset     Down + remove volumes"
	@echo "  clean     Remove caches and build artifacts"

up:
	$(COMPOSE) up -d
	@bash scripts/verify_attendee_codespace.sh || true

down:
	$(COMPOSE) down

restart: down up

smoke:
	pytest -v tests/test_e2e_smoke.py

test:
	pytest -v

lint:
	ruff check .

format:
	ruff check --fix .
	black .

reset:
	$(COMPOSE) down -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .ruff_cache -exec rm -rf {} +
	rm -rf build/ dist/ *.egg-info
