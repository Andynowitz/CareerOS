# CareerOS

**CareerOS is a full-stack career management platform for organizing job applications, resumes, and AI-powered career insights.**

Built with a modern TypeScript/Python stack, CareerOS combines application tracking, resume management, deterministic job matching, and intelligent workflow assistance in one platform.

## Current Status

**Phase 6 — Application Intelligence & Workflow: Complete ✅**

Implemented functionality includes:

* Job and application management
* Application activity timeline
* Resume upload, versioning, and processing
* AI-powered job and resume analysis
* Deterministic job/resume matching
* Application dashboards and insights
* Application assistant and follow-up tracking
* Advanced job filtering and sorting

**Next:** Phase 7 — Production Readiness

## Tech Stack

| Layer           | Technology                                     |
| --------------- | ---------------------------------------------- |
| Frontend        | Next.js 15, React 19, TypeScript, Tailwind CSS |
| Backend         | FastAPI, Python 3.13, Pydantic                 |
| Database        | PostgreSQL 17, SQLAlchemy 2, Alembic           |
| Authentication  | Better Auth                                    |
| Background Jobs | Redis 7, Celery                                |
| Object Storage  | MinIO                                          |
| Testing         | Vitest, React Testing Library, pytest          |
| Quality         | ESLint, Ruff, mypy                             |
| Infrastructure  | Docker Compose                                 |
| CI              | GitHub Actions                                 |

## Architecture

```text
Browser
   │
   ▼
Next.js ────── Better Auth
   │
   ▼
FastAPI
   │
   ├── PostgreSQL
   ├── Redis ── Celery
   └── MinIO
```

CareerOS is organized as a pnpm/Turborepo monorepo:

```text
careeros/
├── apps/
│   ├── web/        # Next.js frontend
│   ├── api/        # FastAPI backend
│   └── extension/  # Browser extension
├── packages/       # Shared packages
├── docs/           # Documentation
└── docker-compose.yml
```

## Getting Started

### Requirements

* Docker Desktop
* Node.js 22 LTS
* pnpm 9

### Setup

```bash
pnpm install
cp .env.example .env
docker compose up -d --build
```

Apply database migrations:

```bash
docker compose exec api alembic upgrade head
```

The application is then available at:

* Web: `http://localhost:3000`
* API: `http://localhost:8000`
* API Docs: `http://localhost:8000/docs`

## Testing

Frontend:

```bash
pnpm --filter web test
pnpm --filter web lint
pnpm --filter web build
```

Backend:

```bash
docker compose exec api pytest -q
```

## Documentation

* [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — system architecture and design
* [`docs/API.md`](docs/API.md) — API overview and conventions
* [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) — development workflow
* [`docs/ROADMAP.md`](docs/ROADMAP.md) — project roadmap

## Engineering Principles

CareerOS emphasizes:

* Clean architecture
* Strict typing
* Explicit validation
* Backend authorization and resource ownership
* Testable business logic
* Reproducible development environments

## License

License information will be added before the first public release.
