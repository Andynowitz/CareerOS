# CareerOS Roadmap

CareerOS is developed incrementally, with each phase building on a tested and stable foundation.

---

## Phase 1 — Foundation ✅

Core project and infrastructure setup.

* pnpm/Turborepo monorepo
* Next.js frontend
* FastAPI backend
* PostgreSQL
* Redis + Celery
* MinIO
* Better Auth
* Docker Compose
* Testing and CI

---

## Phase 2 — Job Management ✅

Core application tracking.

* Job CRUD
* Application statuses
* Job activity tracking
* Job detail views
* Authentication and resource ownership
* Backend and frontend tests

---

## Phase 3 — Resume Management ✅

Resume storage and processing.

* PDF/DOCX uploads
* File validation
* Text extraction
* Resume versioning
* MinIO storage
* Resume API and UI
* Automated tests

---

## Phase 4 — AI Analysis ✅

AI-powered analysis of jobs and resumes.

* Job description analysis
* Resume analysis
* Structured job insights
* AI-generated insights
* Asynchronous processing
* Persistent analysis history
* Automated tests

---

## Phase 5 — Job Matching ✅

Deterministic and explainable job/resume matching.

* Skill matching and normalization
* Required/preferred skill handling
* Experience and education matching
* Deterministic scoring
* Match explanations
* Match persistence and history
* Backend API and frontend integration
* Automated testing

### Design Goals

The matching engine is:

* **Deterministic** — identical inputs produce identical results
* **Reproducible** — results can be recalculated
* **Explainable** — users can understand the score
* **Testable** — matching rules are covered by automated tests

---

## Phase 6 — Application Intelligence & Workflow ✅

Improved application tracking and workflow management.

* Application dashboard
* Application statistics and funnel metrics
* Activity timeline and filtering
* Application insights
* Job-specific application assistant
* Follow-up tracking
* Advanced job filtering
* Match-score filtering
* Sorting and status/date filters
* Frontend and backend testing
* Production build verification

---

## Phase 7 — Production Readiness ⏳

Prepare CareerOS for production use.

* End-to-end testing
* Accessibility improvements
* Performance optimization
* Security hardening
* Rate limiting
* Production deployment
* Monitoring and error tracking
* CI/CD improvements
* Final documentation

---

## Development Workflow

Each phase follows:

**Plan → Implement → Test → Document → CI → Complete**

Existing functionality should remain stable as new phases are introduced.
