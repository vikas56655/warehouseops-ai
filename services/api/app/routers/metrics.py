from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1", tags=["demo"])

class Metric(BaseModel):
    name: str
    value: float
    unit: str
    provenance: str

@router.get("/metrics", response_model=list[Metric])
def demo_metrics() -> list[Metric]:
    """Seeded illustrative figures only; not connected to operational data."""
    return [
        Metric(name="Orders", value=12480, unit="orders", provenance="synthetic_demo"),
        Metric(name="Backlog", value=420, unit="orders", provenance="synthetic_demo"),
        Metric(name="Throughput", value=935, unit="orders/hour", provenance="synthetic_demo"),
        Metric(name="Capacity utilization", value=78.4, unit="percent", provenance="synthetic_demo"),
    ]
