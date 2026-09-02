# CareerOS

CareerOS is an intelligent job search and career management platform for managing job applications, resumes, job descriptions, interviews, and AI-powered career analysis.

The project is built as a production-oriented full-stack monorepo with a Next.js frontend, FastAPI backend, PostgreSQL database, Redis/Celery background processing, and Better Auth authentication.

## Project Status

| Phase                       | Status     |
| --------------------------- | ---------- |
| Phase 1 — Foundation        | ✅ Complete |
| Phase 2 — Core Application  | ⏳ Planned  |
| Phase 3 — Resume Management | ⏳ Planned  |
| Phase 4 — AI Analysis       | ⏳ Planned  |
| Phase 5 — Job Matching      | ⏳ Planned  |
| Phase 6 — Browser Extension | ⏳ Planned  |
| Phase 7 — Finalization      | ⏳ Planned  |

---

## Phase 1 — Foundation

Phase 1 establishes the technical foundation required for the rest of the platform.

### Technology Stack

* **Monorepo:** Turborepo + pnpm 9
* **Runtime:** Node.js 22 LTS
* **Frontend:** Next.js 15, React 19, TypeScript
* **Backend:** FastAPI, Python 3.13
* **Database:** PostgreSQL 17
* **ORM:** SQLAlchemy 2
* **Migrations:** Alembic
* **Authentication:** Better Auth
* **Caching / messaging:** Redis 7
* **Background jobs:** Celery
* **Object storage:** MinIO
* **Testing:** Vitest, React Testing Library, pytest
* **Quality:** ESLint, Ruff, mypy
* **Infrastructure:** Docker Compose
* **CI:** GitHub Actions

### Phase 1 Features

* Production-oriented monorepo structure
* Dockerized development environment
* PostgreSQL database
* Redis and Celery worker
* FastAPI API foundation
* Next.js application foundation
* Better Auth email/password authentication
* Google OAuth configuration
* PostgreSQL-backed authentication sessions
* Protected dashboard route
* FastAPI authentication boundary
* SQLAlchemy database foundation
* Alembic migration infrastructure
* MinIO object storage foundation
* OpenAPI / Swagger / ReDoc documentation
* Frontend and backend testing foundations
* ESLint, Ruff and mypy configuration
* GitHub Actions CI pipeline
* Environment-based configuration

---

## Repository Structure

```text
careeros/
├── apps/
│   ├── web/                 # Next.js frontend
│   ├── api/                 # FastAPI backend
│   └── extension/           # Browser extension
│
├── packages/
│   ├── types/               # Shared TypeScript types
│   ├── eslint-config/       # Shared ESLint configuration
│   └── config/              # Shared project configuration
│
├── docs/                    # Project documentation
├── docker/                  # Docker-related configuration
├── .github/                 # GitHub Actions
│
├── docker-compose.yml
├── package.json
├── pnpm-workspace.yaml
├── turbo.json
└── README.md
```

---

## Prerequisites

* Docker Desktop with Docker Compose
* Node.js 22 LTS
* pnpm 9

Verify your versions:

```bash
node --version
pnpm --version
docker --version
docker compose version
```

CareerOS currently targets Node.js 22.

---

## Configuration

Copy the environment template:

```bash
cp .env.example .env
```

Never commit `.env` or other files containing secrets.

The main configuration includes:

```env
POSTGRES_USER=careeros
POSTGRES_PASSWORD=change_this_password
POSTGRES_DB=careeros

DATABASE_URL=postgresql+asyncpg://careeros:change_this_password@postgres:5432/careeros

REDIS_URL=redis://redis:6379/0

BETTER_AUTH_SECRET=replace_with_a_32_character_random_secret
BETTER_AUTH_URL=http://localhost:3000

GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

MINIO_ROOT_USER=careeros
MINIO_ROOT_PASSWORD=change_this_password
MINIO_ENDPOINT=minio:9000
MINIO_BUCKET=careeros-files

NEXT_PUBLIC_API_URL=http://localhost:8000
API_CORS_ORIGINS=http://localhost:3000
```

The web application may use a separate PostgreSQL connection string when running Better Auth directly inside the Next.js container.

---

## Running CareerOS

Install JavaScript dependencies:

```bash
pnpm install
```

Start the development infrastructure:

```bash
docker compose up --build
```

### Services

| Service       | URL                                |
| ------------- | ---------------------------------- |
| Web           | http://localhost:3000              |
| FastAPI       | http://localhost:8000              |
| Swagger       | http://localhost:8000/docs         |
| ReDoc         | http://localhost:8000/redoc        |
| OpenAPI       | http://localhost:8000/openapi.json |
| MinIO Console | http://localhost:9001              |

PostgreSQL and Redis are also exposed locally for development.

---

## Database

Run the current Alembic migrations:

```bash
docker compose exec api alembic upgrade head
```

Check migration status:

```bash
docker compose exec api alembic current
```

Verify that models and migrations are synchronized:

```bash
docker compose exec api alembic check
```

After changing SQLAlchemy models, generate a migration:

```bash
docker compose exec api alembic revision --autogenerate -m "description"
```

Always review generated migrations before applying them.

Authentication tables are managed by Better Auth. CareerOS application tables will be introduced through subsequent application migrations.

---

## Authentication

Better Auth is the authentication owner of the Next.js application.

Phase 1 provides:

* Email/password registration
* Email/password login
* PostgreSQL-backed sessions
* Google OAuth configuration
* Protected dashboard access
* Secure session handling
* FastAPI authentication validation

Authentication is intentionally not duplicated in FastAPI.

The backend validates the authenticated session and remains responsible for API authorization, resource ownership, and access control as application features are introduced.

---

## API

The FastAPI backend uses the versioned API namespace:

```text
/api/v1/
```

Available documentation:

```text
/api/v1/
/docs
/redoc
/openapi.json
```

The API exposes a health endpoint and database connectivity foundation during Phase 1.

Detailed API documentation is maintained in:

```text
docs/API.md
```

---

## Testing

### Frontend

```bash
pnpm --filter web test
```

### Frontend linting

```bash
pnpm --filter web lint
```

### Frontend production build

```bash
pnpm --filter web build
```

### Backend tests

```bash
cd apps/api
pytest
```

### Backend linting

```bash
cd apps/api
ruff check .
```

### Backend type checking

```bash
cd apps/api
mypy app
```

### Full workspace checks

From the repository root:

```bash
pnpm lint
pnpm test
pnpm build
```

---

## CI

CareerOS uses GitHub Actions for continuous integration.

CI runs on:

* Pushes to `main`
* Pull requests

The current pipeline verifies:

### Frontend

* Dependency installation
* ESLint
* Vitest
* Production build

### Backend

* Ruff
* mypy
* pytest

The CI environment uses:

* Node.js 22
* pnpm 9
* Python 3.13

Dependencies are installed using the repository lockfile to ensure reproducible builds.

---

## Development Principles

CareerOS follows several engineering principles:

* TypeScript strict mode
* No unnecessary `any`
* SOLID principles
* Separation of concerns
* Environment-driven configuration
* External input validation
* API authentication and authorization
* Resource ownership checks
* Business logic outside UI components and API controllers
* Testable services and modules
* Dockerized development infrastructure
* Reproducible CI builds

---

## Roadmap

### Phase 1 — Foundation ✅

Establish the complete development and infrastructure foundation.

### Phase 2 — Core Application

Planned features:

* Dashboard
* Job CRUD
* Job statuses
* Kanban board
* Search and filtering
* Application tracking
* Activity tracking

### Phase 3 — Resume Management

Planned features:

* Resume upload
* Resume storage
* Resume metadata
* Resume management UI
* Resume parsing foundation

### Phase 4 — AI Analysis

Planned features:

* Job description analysis
* Resume analysis
* AI-generated insights
* Background AI processing
* Analysis history

### Phase 5 — Job Matching

Planned features:

* Deterministic job/resume matching
* Match scoring
* Skill comparison
* Match explanations
* Application recommendations

### Phase 6 — Browser Extension

Planned features:

* Job-page detection
* Job description extraction
* CareerOS integration
* One-click job saving

### Phase 7 — Finalization

Planned work:

* Performance optimization
* Security hardening
* Accessibility improvements
* Production deployment
* Documentation completion
* End-to-end testing
* Final CI/CD improvements

---

## Project Documentation

Additional documentation is located in:

```text
docs/
```

Recommended documentation structure:

```text
docs/
├── API.md
├── ARCHITECTURE.md
├── DEVELOPMENT.md
└── ROADMAP.md
```

The root `README.md` provides the project overview and current status, while detailed technical documentation belongs in `docs/`.

---

## License

License information will be added before the first public release.
