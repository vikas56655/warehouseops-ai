from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import check_database
from app.routers.metrics import router as metrics_router
from app.routers.operations import router as operations_router
from app.routers.simulation import router as simulation_router

app = FastAPI(title="WarehouseOps AI API", version="0.3.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[s.strip() for s in settings.cors_origins.split(",") if s.strip()],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["Content-Type"],
)
app.include_router(metrics_router)
app.include_router(operations_router)
app.include_router(simulation_router)

@app.get("/health/live")
def liveness() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/health/ready")
def readiness() -> dict[str, str]:
    try:
        if not check_database():
            raise RuntimeError("Unexpected database response")
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    return {"status": "ready"}
