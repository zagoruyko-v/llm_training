# Makefile for LLM Platform

.PHONY: lint format test precommit-install clean up

lint:
	@echo 'Running linters (ruff, black, isort)...'
	ruff .
	black --check .
	isort --check-only .

format:
	@echo 'Formatting code (black, isort)...'
	black .
	isort .

test:
	@echo 'Running backend tests...'
	pytest
	@echo 'Running Django admin tests...'
	docker compose exec admin python manage.py test

precommit-install:
	@echo 'Installing pre-commit hooks...'
	pre-commit install

clean:
	@echo 'Cleaning up __pycache__, .pyc, and build artifacts...'
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type f -name '*.pyd' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} +
	find . -type d -name 'dist' -exec rm -rf {} +
	find . -type d -name 'build' -exec rm -rf {} +

up:
	docker compose up -d --build
