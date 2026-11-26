"""Reproducible discrete-event warehouse model; assumptions are synthetic."""
import random
from typing import Literal

import simpy
from pydantic import BaseModel, Field


class Scenario(BaseModel):
    seed: int = 42
    season: Literal["summer", "winter"] = "winter"
    shift_minutes: int = Field(default=480, ge=60, le=1440)
    arrivals_per_hour: float = Field(default=30, gt=0, le=300)
    pickers: int = Field(default=5, ge=1, le=100)
    receivers: int = Field(default=2, ge=1, le=100)
    dispatchers: int = Field(default=2, ge=1, le=100)


def simulate(scenario: Scenario) -> dict:
    rng = random.Random(scenario.seed)
    env = simpy.Environment()
    resources = {
        "reception": simpy.Resource(env, capacity=scenario.receivers),
        "picking": simpy.Resource(env, capacity=scenario.pickers),
        "dispatch": simpy.Resource(env, capacity=scenario.dispatchers),
    }
    stats = {zone: {"completed": 0, "wait_minutes": 0.0, "busy_minutes": 0.0,
                    "peak_queue": 0} for zone in resources}
    arrivals = completed = units_done = colis_done = 0
    cycle_times = []
    winter = scenario.season == "winter"

    def order(units, colis):
        nonlocal completed, units_done, colis_done
        start = env.now
        durations = {"reception": 0.8 + colis * 0.45,
                     "picking": 1.2 + units * 0.18 + colis * (1.15 if winter else 0.55),
                     "dispatch": 0.6 + colis * 0.35}
        for zone, resource in resources.items():
            queued = env.now
            row = stats[zone]
            with resource.request() as request:
                row["peak_queue"] = max(row["peak_queue"], len(resource.queue))
                yield request
                row["wait_minutes"] += env.now - queued
                service = durations[zone] * rng.uniform(0.8, 1.2)
                row["busy_minutes"] += min(service, scenario.shift_minutes - env.now)
                yield env.timeout(service)
                row["completed"] += 1
        completed += 1
        units_done += units
        colis_done += colis
        cycle_times.append(env.now - start)

    def source():
        nonlocal arrivals
        while True:
            yield env.timeout(rng.expovariate(scenario.arrivals_per_hour / 60))
            arrivals += 1
            units = rng.randint(5, 40)
            capacity = 5 if winter else 10
            colis = (units + capacity - 1) // capacity
            env.process(order(units, colis))

    env.process(source())
    env.run(until=scenario.shift_minutes)
    zones = []
    for zone, resource in resources.items():
        row = stats[zone]
        zones.append({"zone": zone, "completed": row["completed"],
                      "total_wait_minutes_for_started": round(row["wait_minutes"], 2),
                      "peak_queue": row["peak_queue"],
                      "utilization": round(row["busy_minutes"] /
                                           (resource.capacity * scenario.shift_minutes), 4)})
    return {"provenance": "synthetic_demo", "scenario": scenario.model_dump(),
            "arrived": arrivals, "completed": completed, "backlog": arrivals - completed,
            "units_dispatched": units_done, "colis_dispatched": colis_done,
            "mean_completed_cycle_minutes": round(sum(cycle_times) / completed, 2)
            if completed else None, "zones": zones}
