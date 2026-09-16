# CareerOS

CareerOS is a full-stack career management platform for tracking job applications, managing resumes, and generating AI-powered career insights.

## Status

| Phase | Status |
|---|---|
| Phase 1 — Foundation | ✅ Complete |
| Phase 2 — Core Application | ✅ Complete |
| Phase 3 — Resume Management | ✅ Complete |
| Phase 4 — AI Analysis | ✅ Complete |
| Phase 5 — Job Matching | 🚧 Next |
| Phase 6 — Browser Extension | ⏳ Planned |
| Phase 7 — Finalization | ⏳ Planned |

## Stack

- **Frontend:** Next.js 15, React 19, TypeScript, Tailwind CSS
- **Backend:** FastAPI, Python 3.13, Pydantic
- **Database:** PostgreSQL 17, SQLAlchemy 2, Alembic
- **Authentication:** Better Auth
- **Background jobs:** Redis 7 + Celery
- **Storage:** MinIO (S3-compatible)
- **Testing:** Vitest, React Testing Library, pytest
- **Quality:** ESLint, Ruff, mypy
- **Infrastructure:** Docker Compose
- **CI:** GitHub Actions

## Features

### Job Management
- Job CRUD with user ownership
- Application statuses
- Activity tracking
- Job detail views
- Protected API endpoints

### Resume Management
- PDF and DOCX uploads
- File validation and size limits
- Text extraction
- Resume versions
- MinIO-backed file storage

### AI Analysis
- Job description analysis
- Resume analysis
- AI-generated job insights
- Asynchronous Celery processing
- Persistent analysis results and history

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

The repository is organized as a Turborepo/pnpm monorepo:

```text
careeros/
├── apps/
│   ├── web/          # Next.js application
│   ├── api/          # FastAPI backend
│   └── extension/    # Browser extension
├── packages/         # Shared packages
├── docs/             # Technical documentation
└── docker-compose.yml
```

## Getting Started

### Requirements

- Docker Desktop
- Node.js 22 LTS
- pnpm 9

### Setup

```bash
pnpm install
cp .env.example .env
docker compose up --build
```

Apply database migrations:

```bash
docker compose exec api alembic upgrade head
```

### Local Services

| Service | URL |
|---|---|
| Web | http://localhost:3000 |
| API | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| MinIO | http://localhost:9001 |

## Testing

```bash
# Frontend
pnpm --filter web test
pnpm --filter web lint
pnpm --filter web build

# Backend
cd apps/api
pytest
ruff check .
mypy app
```

Or run the workspace checks:

```bash
pnpm lint
pnpm test
pnpm build
```

## Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — system structure and responsibilities
- [`docs/API.md`](docs/API.md) — API endpoints and conventions
- [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) — local development and quality checks
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — implementation roadmap

## Engineering Principles

CareerOS emphasizes clean architecture, strict typing, validated inputs, backend authorization, resource ownership, testable components, and reproducible development environments.

## License

License information will be added before the first public release.
