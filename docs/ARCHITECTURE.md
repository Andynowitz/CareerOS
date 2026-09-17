# CareerOS Architecture

CareerOS is a full-stack application organized as a pnpm/Turborepo monorepo. The architecture separates the web application, API, background processing, persistence, and storage layers.

## System Overview

```text
                         ┌───────────────┐
                         │    Browser    │
                         └───────┬───────┘
                                 │
                                 ▼
                         ┌───────────────┐
                         │   Next.js     │
                         │ React + TS    │
                         └───────┬───────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
              Better Auth               FastAPI API
                    │                         │
                    └────────────┬────────────┘
                                 ▼
                            PostgreSQL
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
                  Redis                    MinIO
                    │
                    ▼
              Celery Worker
```

## Monorepo

```text
careeros/
├── apps/
│   ├── web/        # Next.js application
│   ├── api/        # FastAPI backend
│   └── extension/  # Browser extension
├── packages/       # Shared packages
├── docs/           # Documentation
├── .github/        # CI configuration
└── docker-compose.yml
```

## Frontend

`apps/web` contains the user-facing application.

Main technologies:

* Next.js
* React
* TypeScript
* Tailwind CSS
* Better Auth
* Zod

Responsibilities include authentication UI, dashboards, job management, resume management, and communication with the backend API.

## Backend

`apps/api` contains the FastAPI application.

The backend follows a layered structure:

```text
app/
├── api/
│   └── v1/
├── core/
├── db/
├── models/
├── repositories/
├── schemas/
├── services/
└── tasks/
```

Responsibilities include:

* API endpoints
* Business logic
* Validation
* Authorization
* Resource ownership
* Database access
* Background processing

Route handlers are intentionally kept thin, with business logic implemented in services.

## Authentication

Better Auth is the central authentication authority.

Authentication data is stored in PostgreSQL. FastAPI validates authenticated sessions and performs authorization and resource ownership checks.

Authentication and authorization remain separate concerns:

* **Authentication:** Who is the user?
* **Authorization:** Is the user allowed to access this resource?

## Background Processing

Redis and Celery are used for asynchronous work such as AI and file processing.

Long-running operations should run outside normal API request handling.

## Storage

PostgreSQL stores application data and metadata.

MinIO provides S3-compatible object storage for uploaded files such as resumes.

File metadata belongs in PostgreSQL while file contents are stored in object storage.

## Infrastructure

Local development uses Docker Compose to provide:

* Web
* API
* PostgreSQL
* Redis
* Celery
* MinIO

This provides a consistent development environment across machines.

## Engineering Principles

CareerOS emphasizes:

* Separation of concerns
* Clean architecture
* Strict typing
* Explicit validation
* Backend authorization
* Resource ownership
* Testable business logic
* Environment-based configuration
* Reproducible development environments
