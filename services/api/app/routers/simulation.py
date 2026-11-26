from typing import Annotated

from fastapi import APIRouter, Query

from app.simulator import Scenario, simulate

router = APIRouter(prefix="/api/v1/simulation", tags=["simulation"])


@router.get("/run")
def run(scenario: Annotated[Scenario, Query()]):
    return simulate(scenario)
