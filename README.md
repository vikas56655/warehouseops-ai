# WarehouseOps AI

> Agentic warehouse operations intelligence — production-oriented engineering portfolio project.

**Status:** Week 4 interactive Control Tower (runtime verification pending). This is a working starter scaffold, **not** a completed AI platform.

## What is implemented
- Next.js 15 / React 19 responsive light Control Tower UI
- FastAPI typed REST endpoint `/api/v1/metrics`
- Liveness `/health/live` and database readiness `/health/ready`
- PostgreSQL 16 service, Docker Compose, example environment configuration
- Backend tests and GitHub Actions CI
- Explicit `synthetic_demo` provenance on all displayed metrics

**Not implemented yet:** public dataset acquisition, full inventory/order models, forecasting, LangGraph agents, MCP, human approvals, authentication, or deployment. These are future milestones.

## Requirements
Docker Desktop or Docker Engine with Compose. Ports 3000, 8000, and 5432 available locally.

## Quick start
```bash
cp .env.example .env
docker compose up --build
```

Open:
- Dashboard: http://localhost:3000
- API docs: http://localhost:8000/docs
- Liveness: http://localhost:8000/health/live
- Database readiness: http://localhost:8000/health/ready

Stop with `docker compose down`. To **delete local database data**, run `docker compose down -v` (destructive).

## Local API tests without Docker
```bash
cd services/api
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -r requirements-dev.txt
ruff check app tests
python -m pytest -q
```
The tests do not need a running database. The readiness endpoint does.

## Project layout
- `apps/web`: Next.js frontend
- `services/api`: FastAPI backend
- `docs/architecture`: architecture and security decisions
- `.github/workflows/ci.yml`: CI checks

## Data ethics
No employer-internal data, personal worker records, or private operational metrics belong in this public repository. Public demo values are synthetic and visibly labeled. Future data ingestion will document provenance, licenses and limitations.

## Roadmap
1. Foundation (this release)
2. Canonical event model and CSV ingestion (partial: public dataset acquisition pending)
3. SimPy warehouse event simulator
4. KPI dashboard and real/simulated provenance
5. Forecasting and backtesting
6. Anomaly detection
7. Staffing optimization and scenario simulation
8. LangGraph agents
9. MCP and memory
10. Human approvals
11. Evaluation, observability and security
12. Deployment and portfolio release

## License
License selection pending. Do not assume permission to reuse proprietary datasets or employer materials.

## Week 2: operational event ingestion

Import the bundled synthetic dataset into the running database:

```bash
docker compose exec api alembic upgrade head
docker compose exec api python -m app.import_events data/demo_events.csv
curl http://localhost:8000/api/v1/operations/summary
```

The importer validates timezone-aware timestamps, zone, units, colis, duration and provenance using Pydantic, rejects duplicate IDs and persists events with SQLAlchemy. The read-only summary groups by zone and provenance and computes units per recorded activity hour (not employee productivity). Schema initialization uses Alembic; public dataset adapters and richer inventory/order tables remain pending. The dashboard now fetches simulation results and imported operational summaries. Tests use SQLite; PostgreSQL integration and CI verification remain outstanding.

## Week 3: synthetic discrete-event simulator

```bash
curl 'http://localhost:8000/api/v1/simulation/run?season=winter&pickers=5&seed=42'
curl 'http://localhost:8000/api/v1/simulation/run?season=summer&pickers=5&seed=42'
```

The SimPy model covers reception, picking and dispatch, with configurable staffing, arrival rate, shift length and season. Outputs include backlog, throughput, cycle time, resource utilization and peak queue. All parameters are synthetic and uncalibrated. See [assumptions](docs/architecture/simulator.md). Run Alembic before importing events; migration adopts compatible Week 2 starter tables. The simulator does not write to the database. Public dataset integration and runtime verification remain pending.

## Week 4: interactive Control Tower

Open http://localhost:3000 after `docker compose up --build`. Configure a shift and run the simulation, or compare summer and winter using the same input parameters. The frontend reads the simulation and operations endpoints directly; imported data requires the migration and import commands above. GitHub Actions now includes PostgreSQL 16 migration, import and API smoke checks. Passing CI and browser execution have not yet been confirmed.
