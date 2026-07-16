.PHONY: setup start stop test lint format

setup:
	@echo "Setting up local environments..."
	copy .env.example .env
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

start:
	@echo "Launching Docker containers..."
	docker compose up -d --build

stop:
	@echo "Stopping Docker containers..."
	docker compose down

test:
	@echo "Running backend test suite..."
	cd backend && pytest
	@echo "Running frontend E2E test suite..."
	cd frontend && npm run test:e2e

lint:
	cd backend && flake8 app tests
	cd frontend && npm run lint

format:
	cd backend && black app tests
	cd frontend && npm run format
