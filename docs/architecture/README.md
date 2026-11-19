# Architecture decision record — Week 1

The repository is a monorepo with Next.js frontend, FastAPI backend, and PostgreSQL.

## Boundaries
- The API owns validation, database access, and (later) authorization.
- The frontend only consumes API responses; it never connects to PostgreSQL.
- Week 1 demo metrics are explicitly marked `synthetic_demo`.
- LangGraph, MCP, Redis, forecasting, and approvals are intentionally not yet implemented.

## Threat model (initial)
- Do not commit secrets or proprietary operational data.
- Bind local Docker ports to loopback.
- Restrict CORS to the configured frontend origin.
- Never expose database credentials in `NEXT_PUBLIC_` variables.
- Future write endpoints require server-side authentication, role checks and audit trails.

## Future architecture
Next.js → FastAPI → LangGraph orchestration → scoped MCP tools → analytics/optimization services → PostgreSQL and artifact storage.
