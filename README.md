# LLM Assistant Platform

![CI](https://github.com/<your-org-or-username>/<repo-name>/actions/workflows/ci.yml/badge.svg)

A production-ready, containerized platform for experimenting with Large Language Models (LLMs) using Ollama, FastAPI, React, and Django admin. Includes robust feedback/evaluation logging, session management, and a modern frontend.

## Features

- FastAPI backend with REST and WebSocket endpoints
- React frontend chat interface
- Django admin for conversation/message/LLM interaction traceability and feedback
- Ollama as the LLM backend (local, Apple Silicon compatible)
- Docker Compose for full stack orchestration
- Pre-commit hooks, linting, and CI/CD
- All interactions logged with metadata and feedback fields

## Prerequisites

- Docker and Docker Compose
- Apple Silicon (M1/M2) Mac or compatible system
- Make (for using the Makefile)
- Python 3.11+ (for local development)
- Node.js 20+ (for frontend dev)

## Quick Start

### Using Docker Compose (Recommended)

```bash
git clone <repository-url>
cd real_ai
make up
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:3000/api
- WebSocket: ws://localhost:3000/ws
- Django Admin: http://localhost:8001

### Local Development

#### Backend
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

#### Django Admin
```bash
cd admin
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8001
```

## Makefile Commands

- `make up` - Build and start all services with Docker Compose
- `make lint` - Run all linters (ruff, black, isort)
- `make format` - Auto-format code (black, isort)
- `make test` - Run all backend and Django tests
- `make precommit-install` - Install pre-commit hooks
- `make clean` - Remove build, cache, and pyc files

## Pre-commit Hooks

Install and activate pre-commit hooks:
```bash
make precommit-install
```
Hooks: black, ruff, isort, trailing-whitespace, end-of-file-fixer

## CI/CD

- GitHub Actions workflow: `.github/workflows/ci.yml`
- Runs lint, test, Docker build, and health checks on every push/PR

## Feedback & Evaluation System

- All LLM interactions are logged in the Django admin (`LLMInteraction` model)
- Feedback fields: score, thumbs up/down, comment, include_in_training
- Admins can review, filter, and export interactions for evaluation or training

## Environment Variables

- See `.env.example` or Docker Compose for required variables:
  - `OLLAMA_HOST`, `OLLAMA_PORT`, `DEFAULT_MODEL`
  - Django: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DJANGO_SECRET_KEY`, etc.

## Contributing

Contributions are welcome! Please submit a Pull Request and ensure all tests and linters pass.

## License

MIT License. See LICENSE file.
