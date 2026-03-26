# Privacy Intake Pack - Phased Roadmap

**Generated:** 2026-03-26
**Status:** Ready for Implementation

---

## Overview

Privacy Intake Pack is a well-designed FastAPI + PostgreSQL application for privacy case management. The architecture is sound (append-only events, worker pattern, Cloudflare Access), but needs production hardening.

This roadmap prioritizes **high impact, low effort** improvements first, then builds depth over 5 phases.

---

## Phase 1: Foundation & Confidence (Week 1-2)

**Goal:** Make the codebase testable and reliable

### Must-Have (P0)

| Task | Effort | Impact | Why |
|------|--------|--------|-----|
| Add pytest structure + fixtures | 2h | High | Can't safely change anything without tests |
| Repository unit tests | 4h | High | Core data layer needs coverage |
| API integration tests | 4h | High | End-to-end confidence before changes |
| Replace `dataclass` with Pydantic models | 1h | High | Runtime validation, OpenAPI docs |

### Should-Have (P1)

| Task | Effort | Impact | Why |
|------|--------|--------|-----|
| Add `app/config.py` with Pydantic Settings | 1h | Medium | Catches config errors at startup |
| Add global exception handlers | 30m | High | Prevents 500 errors leaking stack traces |
| Add structured JSON logging | 1h | Medium | Debugging in production needs logs |
| Add `pytest.ini` + coverage config | 30m | Medium | Track test coverage |

### Files to Create

```
tests/
├── __init__.py
├── conftest.py          # Fixtures, test DB setup
├── test_repository.py   # Data layer tests
├── test_api.py          # Endpoint tests
└── test_worker.py       # Worker tests (mocked)

app/
├── config.py            # Pydantic Settings
├── schemas.py           # Pydantic request/response models
└── exceptions.py        # Custom exceptions

pytest.ini               # Pytest config
.coveragerc              # Coverage config
```

### Deliverables

- [ ] `pytest` runs successfully
- [ ] Coverage > 60% on core modules
- [ ] All endpoints return proper HTTP status codes
- [ ] Invalid input returns 422, not 500
- [ ] Config validation fails fast on missing env vars

---

## Phase 2: Security Hardening (Week 3-4)

**Goal:** Production-ready security posture

### Must-Have (P0)

| Task | Effort | Impact | Why |
|------|--------|--------|-----|
| Add session-based auth (FastAPI-Users) | 6h | Critical | No auth = no production |
| Cloudflare Access header integration | 2h | High | Identity from Access headers |
| Role-based access (admin/analyst/viewer) | 4h | High | Least privilege |

### Should-Have (P1)

| Task | Effort | Impact | Why |
|------|--------|--------|-----|
| CSRF protection for form submissions | 2h | High | Prevent cross-site attacks |
| Rate limiting on API endpoints | 2h | Medium | Prevent abuse |
| Security headers middleware | 1h | Medium | CSP, XSS protection |
| Input sanitization (HTML in descriptions) | 1h | Medium | Prevent XSS |

### Could-Have (P2)

| Task | Effort | Impact | Why |
|------|--------|--------|-----|
| Access audit logging | 3h | Medium | Track who viewed what |
| Docker secrets support | 2h | Low | Better secrets management |

### Files to Create

```
app/
├── auth/
│   ├── __init__.py
│   ├── session.py      # Session management
│   ├── roles.py        # Role decorators
│   └── cloudflare.py   # Access header parsing
├── middleware.py       # Security headers
└── dependencies.py    # Auth dependencies

requirements.txt        # Add: fastapi-users, itsdangerous, bleach
```

### Deliverables

- [ ] All write endpoints require authentication
- [ ] Roles restrict access appropriately
- [ ] CSRF tokens on all forms
- [ ] Rate limiting on create/update endpoints
- [ ] Security headers in all responses

---

## Phase 3: UX & Functionality (Week 5-6)

**Goal:** Make it usable for real work

### Must-Have (P1)

| Task | Effort | Impact | Why |
|------|--------|--------|-----|
| Extract inline CSS to static files | 1h | Medium | Maintainability |
| Add pagination to case list | 3h | High | Scale beyond 100 cases |
| Add case search/filter | 4h | High | Find cases efficiently |
| Add case edit functionality | 4h | High | Mistakes happen |
| Add `base.html` template layout | 1h | Medium | DRY templates |

### Should-Have (P2)

| Task | Effort | Impact | Why |
|------|--------|--------|-----|
| Dashboard with metrics | 4h | Medium | Visibility |
| Task assignment UI | 3h | Medium | Workflow management |
| CSV export for cases | 2h | Medium | Reporting needs |

### Could-Have (P3)

| Task | Effort | Impact | Why |
|------|--------|--------|-----|
| Email notifications for new cases | 4h | Low | Async awareness |
| PDF export for cases | 3h | Low | External reporting |

### Files to Create

```
app/
├── static/
│   ├── css/main.css
│   └── js/main.js
├── templates/
│   ├── base.html          # Layout template
│   ├── dashboard.html     # Metrics view
│   └── edit_case.html     # Edit form
└── api/
    ├── __init__.py
    ├── cases.py            # REST CRUD
    └── export.py           # CSV/PDF export
```

### Deliverables

- [ ] Case list paginates (20 per page)
- [ ] Search by case_ref, title, submitted_by
- [ ] Filter by status, urgency, request_type
- [ ] Edit case details after creation
- [ ] Dashboard shows case counts by status

---

## Phase 4: Operations & Observability (Week 7-8)

**Goal:** Production-ready operations

### Must-Have (P1)

| Task | Effort | Impact | Why |
|------|--------|--------|-----|
| Prometheus metrics endpoint | 3h | High | Observe what's happening |
| Worker graceful shutdown | 2h | High | Don't lose in-flight work |
| Worker retry with backoff | 3h | High | Handle transient failures |
| Structured JSON logging | 1h | Medium | Parseable logs |

### Should-Have (P2)

| Task | Effort | Impact | Why |
|------|--------|--------|-----|
| OpenTelemetry tracing | 4h | Medium | Distributed debugging |
| Dead letter queue for failed tasks | 4h | Medium | Don't silently fail |
| Alerting rules (Prometheus) | 2h | Medium | Know when things break |

### Could-Have (P3)

| Task | Effort | Impact | Why |
|------|--------|--------|-----|
| Automated backup verification | 3h | Low | Trust but verify |
| Restore procedure test | 2h | Low | Know it works |

### Files to Create

```
app/
├── metrics.py          # Prometheus metrics
├── worker/
│   ├── __init__.py
│   ├── main.py         # Refactored worker
│   ├── retry.py        # Retry logic
│   └── shutdown.py    # Graceful shutdown
└── tracing.py          # OpenTelemetry setup

ops/
├── prometheus.yml      # Prometheus config
└── alerts.yml          # Alerting rules
```

### Deliverables

- [ ] `/metrics` endpoint exposes counters/gauges
- [ ] Worker handles SIGTERM gracefully
- [ ] Failed tasks retry 3x with exponential backoff
- [ ] All logs in JSON format with structured fields

---

## Phase 5: Integration & Extensibility (Week 9-10)

**Goal:** Connect to privacy ecosystem

### Must-Have (P1)

| Task | Effort | Impact | Why |
|------|--------|--------|-----|
| OpenClaw privacy skill integration | 4h | High | Real automation |
| API key authentication | 3h | High | Machine-to-machine |
| OpenAPI/Swagger UI | 2h | Medium | API discoverability |

### Should-Have (P2)

| Task | Effort | Impact | Why |
|------|--------|--------|-----|
| Webhook for task completion | 3h | Medium | Event-driven integration |
| Per-API-key rate limiting | 2h | Medium | Fair use enforcement |

### Could-Have (P3)

| Task | Effort | Impact | Why |
|------|--------|--------|-----|
| Integration documentation | 4h | Low | Self-service |
| API usage examples | 2h | Low | Adoption |

### Files to Create

```
app/
├── api/
│   ├── __init__.py
│   ├── keys.py         # API key management
│   └── webhooks.py     # Webhook delivery
├── integrations/
│   ├── __init__.py
│   └── openclaw.py     # Skill handoff
└── docs/
    └── api.md          # Integration guide
```

### Deliverables

- [ ] Worker hands off to OpenClaw privacy skill
- [ ] API keys can be created/revoked
- [ ] `/docs` shows OpenAPI spec
- [ ] Webhook fires on task completion

---

## Quick Wins (Do Immediately)

These are high-value, low-effort improvements that can be done in a single session:

| Task | Effort | File | Impact |
|------|--------|------|--------|
| Add Pydantic schemas | 1h | `app/schemas.py` | Validation + docs |
| Add global exception handler | 30m | `app/main.py` | No 500 stack traces |
| Add structured logging | 30m | `app/main.py` | Debuggable |
| Add pagination | 1h | `app/repository.py` | Scale |
| Extract CSS | 30m | `app/static/css/main.css` | Maintainability |
| Add base template | 30m | `app/templates/base.html` | DRY |

**Total: ~4 hours for all quick wins**

---

## Architecture Decisions

### Keep
- Monolith structure (appropriate for scale)
- Worker pattern (solid)
- Event-sourced approach (excellent audit trail)
- Cloudflare Access (identity layer)

### Add
- Alembic for migrations (Phase 1)
- FastAPI-Users for auth (Phase 2)
- Static file serving (Phase 3)
- Prometheus metrics (Phase 4)

### Future Considerations
- If scaling: separate API/Worker containers
- If complex workflows: state machine library
- If multi-tenant: tenant isolation at DB level

---

## Metrics to Track

| Metric | Type | Target | Phase |
|--------|------|--------|-------|
| Case creation latency | Latency | < 200ms p95 | 4 |
| Task processing latency | Latency | < 5s p95 | 4 |
| API error rate | Error | < 0.1% | 4 |
| Worker failure rate | Error | < 1% | 4 |
| Test coverage | Quality | > 80% | 1 |
| Auth coverage | Security | 100% write endpoints | 2 |

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Auth implementation complexity | Medium | High | Use FastAPI-Users, don't roll own |
| Worker data loss on crash | High | Medium | Graceful shutdown + retry (Phase 4) |
| DB migration failure | Medium | High | Alembic + backup before migration |
| Performance at scale | Low | Medium | Pagination + indexes already done |

---

## Success Criteria

Each phase is complete when:

**Phase 1:** Tests pass, coverage > 60%, input validation works
**Phase 2:** Auth required for writes, roles enforced, CSRF protected
**Phase 3:** Case list paginates, search works, edits save correctly
**Phase 4:** Metrics exposed, worker resilient, logs structured
**Phase 5:** OpenClaw integration works, API keys functional

---

## Suggested Sprint Plan

### Week 1-2: Phase 1
- Day 1-2: Pytest setup, fixtures, initial tests
- Day 3-4: Pydantic models, config validation
- Day 5: Exception handling, logging

### Week 3-4: Phase 2
- Day 1-3: FastAPI-Users setup, session auth
- Day 4: Cloudflare Access integration
- Day 5: Roles, CSRF, rate limiting

### Week 5-6: Phase 3
- Day 1-2: Static assets, pagination, search
- Day 3-4: Case editing, dashboard
- Day 5: Polish, testing

### Week 7-8: Phase 4
- Day 1-2: Prometheus metrics
- Day 3-4: Worker hardening
- Day 5: Logging, alerting

### Week 9-10: Phase 5
- Day 1-2: OpenClaw integration
- Day 3-4: API keys, webhooks
- Day 5: Documentation, testing

---

## Next Action

**Start here:** Add pytest structure + Pydantic schemas

```bash
# Create test structure
mkdir -p tests
touch tests/__init__.py tests/conftest.py tests/test_repository.py tests/test_api.py

# Create app modules
touch app/schemas.py app/config.py app/exceptions.py

# Add pytest config
cat > pytest.ini << 'EOF'
[pytest]
testpaths = tests
python_files = test_*.py
addopts = -v --tb=short
EOF
```

Then implement the quick wins (4 hours total) before moving to Phase 1 proper.