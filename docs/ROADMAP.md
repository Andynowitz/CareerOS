# CareerOS Roadmap

CareerOS is developed in incremental phases. Each phase should leave the project in a stable, tested state before the next phase begins.

---

## Phase 1 — Foundation ✅

Project and infrastructure foundation.

* [x] pnpm monorepo
* [x] Next.js frontend
* [x] FastAPI backend
* [x] PostgreSQL
* [x] Redis + Celery
* [x] MinIO
* [x] Better Auth
* [x] Docker Compose
* [x] Testing and code-quality tooling
* [x] GitHub Actions CI

---

## Phase 2 — Job Management ✅

Core job application tracking.

* [x] Job CRUD
* [x] Application statuses
* [x] Job activity tracking
* [x] Job detail views
* [x] Authentication and resource ownership
* [x] Backend tests
* [x] Frontend tests

---

## Phase 3 — Resume Management ✅

Resume storage, versioning, and processing.

* [x] PDF/DOCX uploads
* [x] File validation
* [x] Text extraction
* [x] Resume versions
* [x] MinIO storage
* [x] Resume API
* [x] Resume UI
* [x] Automated tests

---

## Phase 4 — AI Analysis ✅

AI-powered analysis of jobs and resumes.

* [x] Job description analysis
* [x] Resume analysis
* [x] Structured job insights
* [x] AI-generated match insights
* [x] OpenAI integration
* [x] Celery-based asynchronous processing
* [x] Redis task coordination
* [x] Persistent analysis results
* [x] Analysis status and history
* [x] Automated tests

---

# Phase 5 — Job Matching 🚧

Build a deterministic and explainable matching system between jobs and resumes.

### 5.1 — Analysis & Design

* [ ] Analyze existing `Job` model
* [ ] Analyze existing `JobAnalysis`
* [ ] Analyze existing `Resume` model
* [ ] Analyze existing `ResumeVersion`
* [ ] Analyze existing `ResumeAnalysis`
* [ ] Analyze existing Phase 4 AI insights
* [x] Define the matching domain model
* [x] Define matching inputs
* [x] Define matching rules
* [x] Define scoring weights
* [x] Define skill normalization strategy
* [x] Define explainable match output

### 5.2 — Matching Engine

* [x] Implement matching domain
* [x] Implement skill matching
* [x] Implement required/preferred skill handling
* [x] Implement experience matching
* [x] Implement education matching
* [x] Implement score calculation
* [x] Implement match explanations
* [x] Add unit tests

### 5.3 — Persistence

* [x] Create match database model
* [x] Create database migration
* [x] Implement match repository
* [x] Implement match persistence
* [x] Implement match history
* [x] Add database tests

### 5.4 — Backend API

* [x] Define matching API
* [x] Implement match creation
* [x] Implement match retrieval
* [x] Implement match history
* [x] Add authorization and ownership checks
* [x] Add API tests
* [x] Update API documentation

### 5.5 — Frontend
- [x] Add match score to job views
- [x] Add match breakdown
- [x] Add matched skills
- [x] Add missing skills
- [x] Add match explanation
- [x] Add resume selection
- [x] Add loading/error states
- [x] Add frontend tests

### 5.6 — Integration & Quality

* [ ] Run full backend test suite
* [ ] Run full frontend test suite
* [ ] Run linting
* [ ] Run type checking
* [ ] Run production build
* [ ] Test complete matching workflow
* [ ] Verify existing Phase 1–4 functionality
* [ ] Update documentation
* [ ] Mark Phase 5 complete

### Design Goal

The matching engine should be:

* **Deterministic** — same inputs produce the same result
* **Reproducible** — results can be recalculated
* **Explainable** — users can understand why a match received its score
* **Testable** — matching rules can be covered with automated tests

AI-generated analysis from Phase 4 may provide structured information used by the matcher, but the final matching score should be calculated by defined and testable rules.

---

## Phase 6 — Browser Extension ⏳

Save job postings directly from supported job platforms.

* [ ] Browser extension foundation
* [ ] Job-page detection
* [ ] Job description extraction
* [ ] CareerOS authentication
* [ ] One-click job saving
* [ ] Supported-site handling
* [ ] Automated tests

---

## Phase 7 — Production Readiness ⏳

Prepare CareerOS for real-world usage.

* [ ] End-to-end testing
* [ ] Accessibility improvements
* [ ] Performance optimization
* [ ] Security hardening
* [ ] Rate limiting
* [ ] Production deployment
* [ ] Monitoring and error tracking
* [ ] CI/CD improvements
* [ ] Final documentation

---

## Development Workflow

Each phase follows the same workflow:

```text
Plan
  ↓
Implement
  ↓
Test
  ↓
Document
  ↓
CI
  ↓
Complete
  ↓
Next Phase
```

Existing functionality must remain stable when introducing a new phase.
