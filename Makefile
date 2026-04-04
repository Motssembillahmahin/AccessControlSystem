.PHONY: help install run migrate migrate-create migrate-down \
        test lint format pre-commit \
        docker-up docker-down docker-build docker-ps

# ── Default ────────────────────────────────────────────────────────────────────
help: ## Show all available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

# ── Setup ──────────────────────────────────────────────────────────────────────
install: ## Install all dependencies via uv
	uv sync

# ── App ────────────────────────────────────────────────────────────────────────
run: ## Start Django dev server at http://localhost:8000
	python manage.py runserver

# ── Database ───────────────────────────────────────────────────────────────────
migrate: ## Apply all pending migrations
	python manage.py migrate

migrate-create: ## Create a new migration  (usage: make migrate-create msg="description")
	python manage.py makemigrations --name "$(msg)"

migrate-down: ## Roll back one migration  (usage: make migrate-down app=accesscontrol)
	python manage.py migrate $(app) --revert

# ── Tests ──────────────────────────────────────────────────────────────────────
test: ## Run the full test suite
	python manage.py test core.accesscontrol.tests

# ── Code quality ───────────────────────────────────────────────────────────────
lint: ## Run ruff linter with auto-fix
	ruff check --fix core/

format: ## Run ruff formatter
	ruff format core/

pre-commit: ## Stage all files and run pre-commit hooks
	git add .
	pre-commit run --all-files

# ── Docker ─────────────────────────────────────────────────────────────────────
docker-up: ## Start all services in the background
	docker-compose up -d

docker-down: ## Stop and remove containers
	docker-compose down

docker-build: ## Rebuild Docker images
	docker-compose build

docker-ps: ## Show running containers
	docker-compose ps
