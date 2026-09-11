# CareerOS Architecture

## Overview

CareerOS is a full-stack career management platform organized as a monorepo.

The architecture separates frontend, backend, infrastructure, shared packages, and browser-extension functionality.

```text
                        ┌─────────────────────┐
                        │       Browser       │
                        └──────────┬──────────┘
                                   │
                                   ▼
                        ┌─────────────────────┐
                        │     Next.js Web     │
                        │   React + TypeScript│
                        └──────────┬──────────┘
                                   │
                     ┌─────────────┴─────────────┐
                     │                           │
                     ▼                           ▼
             Better Auth                  FastAPI API
             Authentication              /api/v1/*
                     │                           │
                     ▼                           ▼
                PostgreSQL ◄────────────────────┘
                     │
                     ├──────────────► Redis
                     │                    │
                     │                    ▼
                     │              Celery Worker
                     │
                     └──────────────► MinIO
```

---

## Monorepo

CareerOS uses Turborepo and pnpm workspaces.

```text
careeros/
├── apps/
│   ├── web/
│   ├── api/
│   └── extension/
│
├── packages/
│   ├── types/
│   ├── eslint-config/
│   └── config/
│
├── docs/
├── docker/
├── .github/
│
├── docker-compose.yml
├── package.json
├── pnpm-workspace.yaml
└── turbo.json
```

### `apps/web`

The web application is built with:

* Next.js
* React
* TypeScript
* Tailwind CSS
* Better Auth
* TanStack Query
* Zod

It is responsible for:

* User interface
* Authentication UI
* Client-side application behavior
* User-facing dashboards
* Communication with the FastAPI backend

### `apps/api`

The backend is built with:

* Python
* FastAPI
* Pydantic
* SQLAlchemy
* Alembic

It is responsible for:

* API endpoints
* Business logic
* Authorization
* Database access
* Resource ownership
* Background task integration

### `apps/extension`

The browser extension will integrate CareerOS with external job websites.

It is intentionally isolated from the main web application.

### `packages`

Shared packages contain reusable configuration and types that can be consumed by multiple applications.

---

## Backend Structure

The FastAPI application follows a layered structure:

```text
app/
├── api/
│   └── v1/
│       ├── endpoints/
│       └── router.py
│
├── core/
│   ├── auth.py
│   └── config.py
│
├── db/
│   ├── base.py
│   └── session.py
│
├── models/
├── repositories/
├── schemas/
├── services/
└── tasks/
```

### API Layer

Route handlers define the HTTP interface.

They should remain thin and delegate business logic to services.

### Schemas

Pydantic schemas define validated API input and output models.

### Services

Services contain application and business logic.

### Repositories

Repositories isolate database access where appropriate.

### Models

SQLAlchemy models represent persistent application data.

### Tasks

Celery tasks contain asynchronous/background work.

---

## Authentication

Better Auth is the central authentication authority.

The architecture intentionally avoids implementing a second authentication system inside FastAPI.

```text
User
 │
 ▼
Next.js
 │
 ▼
Better Auth
 │
 ▼
PostgreSQL
 │
 └── User + Session
```

FastAPI validates authenticated sessions before allowing protected resources to be accessed.

Authentication and authorization are separate concerns:

* **Authentication:** Who is the user?
* **Authorization:** Is this user allowed to access this resource?

FastAPI is responsible for authorization and ownership checks.

---

## Data Layer

PostgreSQL is the primary relational database.

SQLAlchemy 2 provides the application ORM layer.

Alembic manages CareerOS database migrations.

Better Auth manages its authentication tables.

CareerOS application tables will be introduced through subsequent migrations.

---

## Background Processing

Redis provides the messaging/backend infrastructure used by Celery.

```text
FastAPI
   │
   ▼
 Redis
   │
   ▼
Celery Worker
   │
   ├── AI processing
   ├── File processing
   └── Other asynchronous jobs
```

Long-running work should not block API requests.

---

## Object Storage

MinIO provides S3-compatible object storage.

It will be used primarily for:

* Resume files
* Uploaded documents
* Other user-generated files

File metadata belongs in PostgreSQL while file contents belong in object storage.

---

## Infrastructure

Local development uses Docker Compose.

Core services include:

* Web
* API
* PostgreSQL
* Redis
* Celery worker
* MinIO

This provides a reproducible development environment across machines.

---

## Engineering Principles

CareerOS follows:

* Separation of concerns
* SOLID principles
* Strict TypeScript
* Explicit validation
* Environment-based configuration
* Secure authentication
* Backend authorization
* Resource ownership checks
* Testable components
* Thin controllers/routes
* Business logic outside UI components
* Reproducible development environments
