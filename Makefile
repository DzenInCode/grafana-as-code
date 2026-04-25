.PHONY: help install generate test up down logs clean

help:
	@echo "Targets:"
	@echo "  install   pip install -e .[dev]"
	@echo "  generate  Render grafanalib dashboards into dashboards/*.json"
	@echo "  test      Run pytest"
	@echo "  up        docker compose up -d (Grafana on http://localhost:3000)"
	@echo "  down      docker compose down"
	@echo "  logs      Tail Grafana logs"
	@echo "  clean     Remove generated dashboard JSON"

install:
	pip install -e ".[dev]"

generate:
	python scripts/generate.py

test:
	pytest -v

up: generate
	docker compose up -d
	@echo "Grafana → http://localhost:3000  (admin / admin)"

down:
	docker compose down

logs:
	docker compose logs -f grafana

clean:
	rm -f dashboards/*.json
