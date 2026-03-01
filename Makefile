PYTHON   := python3
VENV     := venv
BIN      := $(VENV)/bin
UVICORN  := $(BIN)/uvicorn
PYTEST   := $(BIN)/pytest
RUFF     := $(BIN)/ruff

.DEFAULT_GOAL := help

.PHONY: help venv install run test test-one lint format clean

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

venv: ## Create Python virtual environment
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip

install: venv ## Install all dependencies (runtime + dev)
	$(BIN)/pip install -e ".[dev]"

run: ## Run the backend API server on port 8000 (auto-reload)
	$(UVICORN) api.main:app --reload --host 0.0.0.0 --port 8000

test: ## Run all tests
	$(PYTEST) tests/ -v

test-one: ## Run a single test file  (usage: make test-one TEST=tests/test_cluster.py)
	$(PYTEST) $(TEST) -v

lint: ## Lint with ruff
	$(RUFF) check src/ tests/

format: ## Format code with ruff
	$(RUFF) format src/ tests/

clean: ## Remove virtualenv and caches
	rm -rf $(VENV) .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
