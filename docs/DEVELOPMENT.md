# Development Guide

This guide covers local development and quality checks for CareerOS.

## Requirements

* Node.js 22 LTS
* pnpm 9
* Python 3.13
* Docker Desktop
* Docker Compose

CareerOS currently targets Node.js 22.

## Setup

Install dependencies:

```bash
pnpm install
```

Create the local environment:

```bash
cp .env.example .env
```

Configure the required environment variables, then start the application:

```bash
docker compose up --build
```

Run database migrations:

```bash
docker compose exec api alembic upgrade head
```

## Development

Start the frontend independently:

```bash
pnpm --filter web dev
```

Start the backend independently:

```bash
cd apps/api
uvicorn app.main:app --reload
```

View Docker services:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs -f
```

## Testing & Quality

Frontend:

```bash
pnpm --filter web test
pnpm --filter web lint
pnpm --filter web build
```

Backend:

```bash
cd apps/api
pytest
ruff check .
mypy app
```

Before submitting changes, ensure tests, linting, type checking, and the production build pass.

## Database

Apply migrations:

```bash
docker compose exec api alembic upgrade head
```

Check migration state:

```bash
docker compose exec api alembic current
```

Create a migration:

```bash
docker compose exec api alembic revision --autogenerate -m "description"
```

Always review generated migrations before applying them.

## Environment Variables

Never commit secrets or local environment files.

Do not commit:

```text
.env
.env.local
```

Use `.env.example` to document required configuration.

Secrets may include:

* Database credentials
* Better Auth secrets
* OAuth credentials
* API keys
* Storage credentials

## Git Workflow

Use feature branches for development:

```bash
git checkout -b feature/your-feature
```

Keep commits focused and include tests for new functionality.

Before opening a pull request:

```bash
pnpm lint
pnpm test
pnpm build
```

Backend tests and quality checks should also pass.

## Docker

Stop services:

```bash
docker compose down
```

Stop services and remove volumes:

```bash
docker compose down -v
```

Use `down -v` carefully because it removes local database and storage data.

## Development Principles

Changes should:

1. Preserve existing functionality.
2. Include tests for new behavior.
3. Follow the existing architecture.
4. Keep business logic outside UI components.
5. Avoid committing secrets or generated files.
6. Update documentation when behavior changes.
