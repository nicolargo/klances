PYTHON      := python3
VENV        := venv
BIN         := $(VENV)/bin
UVICORN     := $(BIN)/uvicorn
PYTEST      := $(BIN)/pytest
RUFF        := $(BIN)/ruff
FRONTEND    := src/frontend
DOCKER_IMG  := klances

.DEFAULT_GOAL := help

.PHONY: help venv install update run build test test-one lint format audit clean docker docker-run

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

venv: ## Create Python virtual environment
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip

install: venv ## Install all dependencies (backend + frontend)
	$(BIN)/pip install -e ".[dev]"
	cd $(FRONTEND) && npm install

update: ## Update all dependencies (backend + frontend)
	$(BIN)/pip install --upgrade -e ".[dev]"
	cd $(FRONTEND) && npm update

audit: ## Check dependencies for known security vulnerabilities
	$(BIN)/pip-audit
	cd $(FRONTEND) && npm audit

run: ## Start the development server (API + frontend watcher) on port 8000
	$(BIN)/klances-dev

build: ## Build the frontend for production and generate OpenAPI spec
	cd $(FRONTEND) && npm run build
	mkdir -p docs
	$(BIN)/python -c "import json; from api.main import app; json.dump(app.openapi(), open('docs/openapi.json', 'w'), indent=2)"

test: ## Run all tests
	$(PYTEST) tests/ -v

test-one: ## Run a single test file  (usage: make test-one TEST=tests/test_cluster.py)
	$(PYTEST) $(TEST) -v

lint: ## Lint with ruff
	$(RUFF) check src/ tests/

format: ## Format code with ruff
	$(RUFF) format src/ tests/

docker: ## Build the Docker image
	docker build -f docker-files/Dockerfile -t $(DOCKER_IMG) .

docker-run: ## Run Klances in Docker (needs ~/.kube/config)
	docker run --rm -p 8000:8000 -v $$HOME/.kube/config:/root/.kube/config:ro $(DOCKER_IMG)

clean: ## Remove virtualenv, caches and frontend build
	rm -rf $(VENV) .pytest_cache .ruff_cache $(FRONTEND)/dist $(FRONTEND)/node_modules
	find . -type d -name __pycache__ -exec rm -rf {} +
