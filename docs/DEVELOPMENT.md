# CareerOS Development Guide

## Prerequisites

Install:

* Node.js 22 LTS
* pnpm 9
* Python 3.13
* Docker Desktop
* Docker Compose

CareerOS currently targets Node.js 22.

---

## Initial Setup

Clone the repository and enter the project directory.

Install JavaScript dependencies:

```bash
pnpm install
```

Create the local environment file:

```bash
cp .env.example .env
```

Configure the required environment variables.

---

## Start the Application

Start all infrastructure:

```bash
docker compose up --build
```

For detached mode:

```bash
docker compose up --build -d
```

View service status:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs -f
```

View logs for a specific service:

```bash
docker compose logs -f api
docker compose logs -f web
docker compose logs -f celery-worker
```

---

## Database Development

Run migrations:

```bash
docker compose exec api alembic upgrade head
```

Check the current migration:

```bash
docker compose exec api alembic current
```

Verify migration consistency:

```bash
docker compose exec api alembic check
```

Generate a migration after changing SQLAlchemy models:

```bash
docker compose exec api alembic revision --autogenerate -m "description"
```

Always review generated migrations before applying them.

---

## Authentication Development

Better Auth is configured in:

```text
apps/web/src/lib/auth.ts
```

The Better Auth route is:

```text
apps/web/src/app/api/auth/[...all]/route.ts
```

The client is configured in:

```text
apps/web/src/lib/auth-client.ts
```

Authentication data is stored in PostgreSQL.

Do not implement a separate password or session system inside FastAPI.

---

## Frontend Commands

Run the development server:

```bash
pnpm --filter web dev
```

Run tests:

```bash
pnpm --filter web test
```

Run linting:

```bash
pnpm --filter web lint
```

Create a production build:

```bash
pnpm --filter web build
```

---

## Backend Commands

Run the API locally:

```bash
cd apps/api
uvicorn app.main:app --reload
```

Run tests:

```bash
cd apps/api
pytest
```

Run Ruff:

```bash
cd apps/api
ruff check .
```

Run mypy:

```bash
cd apps/api
mypy app
```

---

## Full Workspace Checks

From the repository root:

```bash
pnpm lint
pnpm test
pnpm build
```

These commands should pass before creating a pull request.

---

## Code Quality

### TypeScript

TypeScript strict mode is enabled.

Avoid:

```typescript
const value: any = ...
```

Prefer explicit types, type guards, schemas, and validated boundaries.

### Python

Python uses strict mypy configuration.

Ruff is used for linting and code quality.

### Validation

External input should be validated before entering application logic.

Frontend validation should use Zod where appropriate.

Backend request validation should use Pydantic.

---

## Environment Variables

Never commit:

```text
.env
.env.local
```

Use:

```text
.env.example
```

to document required configuration without storing secrets.

Secrets include:

* Database passwords
* Better Auth secrets
* OAuth credentials
* API keys
* Storage credentials

---

## Docker

Rebuild services after dependency or Dockerfile changes:

```bash
docker compose up --build
```

Rebuild a single service:

```bash
docker compose up --build api
```

Stop services:

```bash
docker compose down
```

Stop services and remove volumes:

```bash
docker compose down -v
```

Use `down -v` carefully because it removes local database and storage data.

---

## Git Workflow

Development should happen on feature branches.

Example:

```bash
git checkout -b feature/jobs-crud
```

Before opening a pull request:

```bash
pnpm lint
pnpm test
pnpm build
```

Backend checks should also pass:

```bash
cd apps/api
ruff check .
mypy app
pytest
```

Commit messages should clearly describe the change.

---

## Pull Requests

A pull request should:

* Have a focused scope
* Include tests for new behavior
* Keep unrelated changes out
* Pass local quality checks
* Pass GitHub Actions CI
* Update documentation when behavior changes

---

## Debugging

Check Docker service status:

```bash
docker compose ps
```

Check API logs:

```bash
docker compose logs api
```

Check frontend logs:

```bash
docker compose logs web
```

Check PostgreSQL:

```bash
docker compose exec postgres pg_isready
```

Check Redis:

```bash
docker compose exec redis redis-cli ping
```

Expected Redis response:

```text
PONG
```

---

## Phase Development

CareerOS is developed incrementally.

Each phase should:

1. Build on the previous phase.
2. Keep existing functionality working.
3. Add tests for new behavior.
4. Update API documentation.
5. Update the root README when project status changes.
6. Keep CI passing.

The root README describes the current overall project state.

Detailed implementation decisions belong in the `docs/` directory.
