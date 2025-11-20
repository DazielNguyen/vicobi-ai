# ===================================================================
# Vicobi AI - Makefile
# ===================================================================

.PHONY: help install dev start test clean docker-up docker-down logs

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "🚀 Vicobi AI - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""

install: ## Install dependencies
	@echo "📦 Installing dependencies..."
	pip install --upgrade pip
	pip install -r requirements.txt
	@echo "✅ Installation complete!"

setup: ## Initial project setup
	@echo "🔧 Setting up project..."
	@if [ ! -f .env ]; then \
		cp .env-example .env; \
		echo "✅ Created .env file from .env-example"; \
		echo "⚠️  Please edit .env and add your API keys"; \
	else \
		echo "ℹ️  .env file already exists"; \
	fi
	@mkdir -p uploads output temp logs
	@echo "✅ Created necessary directories"
	@echo "✅ Setup complete!"

dev: ## Start development server with auto-reload
	@echo "🚀 Starting development server..."
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

start: ## Start production server
	@echo "🚀 Starting production server..."
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

test: ## Run tests
	@echo "🧪 Running tests..."
	pytest -v

lint: ## Run linting
	@echo "🔍 Running linter..."
	flake8 app/ --max-line-length=120 --exclude=__pycache__,*.pyc
	@echo "✅ Linting complete!"

format: ## Format code with black
	@echo "🎨 Formatting code..."
	black app/
	@echo "✅ Formatting complete!"

clean: ## Clean temporary files
	@echo "🧹 Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf temp/*
	@echo "✅ Cleanup complete!"

docker-up: ## Start Docker services (MongoDB)
	@echo "🐳 Starting Docker services..."
	docker compose up -d
	@echo "✅ Docker services started!"

docker-down: ## Stop Docker services
	@echo "🐳 Stopping Docker services..."
	docker compose down
	@echo "✅ Docker services stopped!"

docker-logs: ## View Docker logs
	docker compose logs -f

logs: ## View application logs
	@echo "📝 Viewing logs (Press Ctrl+C to exit)..."
	tail -f logs/api.log

shell: ## Open Python shell with app context
	@echo "🐍 Opening Python shell..."
	python -i -c "from app.config import settings; from app.database import *; print('Settings and database imported')"

info: ## Show project info
	@echo "ℹ️  Vicobi AI - Project Information"
	@echo "================================"
	@echo "Python version: $$(python --version)"
	@echo "Pip version: $$(pip --version | cut -d' ' -f2)"
	@echo "Virtual env: $${VIRTUAL_ENV:-Not activated}"
	@echo ""
	@if [ -f .env ]; then \
		echo "Environment: $$(grep ENVIRONMENT .env | cut -d= -f2)"; \
		echo "API Port: $$(grep API_PORT .env | cut -d= -f2)"; \
	fi

migrate: ## Run database migrations (placeholder)
	@echo "🗄️  Running migrations..."
	@echo "⚠️  No migrations configured yet"

backup: ## Backup MongoDB
	@echo "💾 Creating MongoDB backup..."
	@mkdir -p backups
	docker exec $$(docker ps -qf "name=mongo") mongodump --out /dump
	@echo "✅ Backup complete!"

requirements: ## Update requirements.txt
	@echo "📋 Updating requirements.txt..."
	pip freeze > requirements.txt
	@echo "✅ Requirements updated!"

venv: ## Create virtual environment
	@echo "🔧 Creating virtual environment..."
	python3 -m venv venv
	@echo "✅ Virtual environment created!"
	@echo "💡 Activate it with: source venv/bin/activate"
