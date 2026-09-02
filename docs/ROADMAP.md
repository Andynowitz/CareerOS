# CareerOS Roadmap

CareerOS is developed incrementally through defined implementation phases.

The goal is to establish a reliable technical foundation first and then build the application features on top of it.

---

## Phase 1 — Foundation

**Status: ✅ Complete**

Establish the production-oriented technical foundation.

### Completed

* [x] Turborepo monorepo
* [x] pnpm workspace
* [x] Node.js 22 configuration
* [x] Next.js 15
* [x] React 19
* [x] TypeScript strict mode
* [x] FastAPI
* [x] Python 3.13
* [x] PostgreSQL 17
* [x] Redis 7
* [x] Celery
* [x] SQLAlchemy 2
* [x] Alembic
* [x] Docker Compose
* [x] MinIO
* [x] Better Auth
* [x] Email/password authentication
* [x] Google OAuth configuration
* [x] PostgreSQL-backed sessions
* [x] Protected dashboard
* [x] FastAPI authentication boundary
* [x] API documentation
* [x] Frontend testing foundation
* [x] Backend testing foundation
* [x] ESLint
* [x] Ruff
* [x] mypy
* [x] GitHub Actions CI
* [x] Environment configuration

---

## Phase 2 — Core Application

**Status: ⏳ Planned**

Build the central job application management functionality.

### Planned Features

* [ ] Dashboard
* [ ] Job CRUD
* [ ] Job status management
* [ ] Kanban board
* [ ] Job search
* [ ] Filtering
* [ ] Sorting
* [ ] Application activity
* [ ] Job detail views
* [ ] API ownership checks
* [ ] Tests for core application functionality

---

## Phase 3 — Resume Management

**Status: ⏳ Planned**

Introduce resume storage and management.

### Planned Features

* [ ] Resume upload
* [ ] Resume metadata
* [ ] MinIO integration
* [ ] Resume management UI
* [ ] File validation
* [ ] File size limits
* [ ] Resume parsing foundation
* [ ] Resume versioning
* [ ] Resume-related API endpoints
* [ ] Tests

---

## Phase 4 — AI Analysis

**Status: ⏳ Planned**

Introduce asynchronous AI-powered analysis.

### Planned Features

* [ ] Job description analysis
* [ ] Resume analysis
* [ ] AI-generated insights
* [ ] OpenAI integration
* [ ] Celery-based AI processing
* [ ] Redis job coordination
* [ ] Analysis persistence
* [ ] Analysis history
* [ ] Error handling and retries
* [ ] AI-related API endpoints
* [ ] Tests

---

## Phase 5 — Job Matching

**Status: ⏳ Planned**

Connect job and resume analysis to produce meaningful matching information.

### Planned Features

* [ ] Deterministic match scoring
* [ ] Skill comparison
* [ ] Experience comparison
* [ ] Job/resume compatibility
* [ ] Match explanations
* [ ] Match history
* [ ] Match API endpoints
* [ ] Dashboard integration
* [ ] Tests

---

## Phase 6 — Browser Extension

**Status: ⏳ Planned**

Allow users to interact with CareerOS directly from supported job websites.

### Planned Features

* [ ] Browser extension foundation
* [ ] Job page detection
* [ ] Job description extraction
* [ ] CareerOS authentication integration
* [ ] Save job from browser
* [ ] API integration
* [ ] Extension UI
* [ ] Supported-site handling
* [ ] Tests

---

## Phase 7 — Finalization

**Status: ⏳ Planned**

Prepare CareerOS for production use.

### Planned Features

* [ ] End-to-end testing
* [ ] Accessibility review
* [ ] Performance optimization
* [ ] Security hardening
* [ ] Rate limiting
* [ ] Production configuration
* [ ] Deployment
* [ ] Monitoring
* [ ] Error tracking
* [ ] Final documentation
* [ ] CI/CD improvements
* [ ] Production readiness review

---

## Development Strategy

Each phase should result in a stable project state.

The general workflow is:

```text
Plan
  ↓
Implement
  ↓
Test
  ↓
Document
  ↓
Run CI
  ↓
Complete Phase
  ↓
Start Next Phase
```

A phase should not be considered complete until its required functionality, tests, quality checks, and documentation are in place.

---

## Current Focus

The current completed milestone is:

**Phase 1 — Foundation**

The next development milestone is:

**Phase 2 — Core Application**

Phase 2 will introduce the actual job application management functionality on top of the foundation established in Phase 1.
