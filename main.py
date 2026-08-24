"""Parallel machine scheduling using a MILP model.

This example considers identical parallel machines. Each job must be assigned to
exactly one machine, and the objective is to minimize the makespan, i.e. the
largest workload assigned to any machine.

The formulation is intentionally compact and suitable for a medium-level
operations research project.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import pulp


@dataclass(frozen=True)
class SchedulingData:
    """Input data for the scheduling problem."""

    jobs: List[str]
    machines: List[str]
    processing_time: Dict[str, int]


def build_sample_data() -> SchedulingData:
    """Create a deterministic, original sample instance.

    The processing times are deliberately unbalanced so that the optimization
    model must distribute long and short jobs across the machines.
    """

    jobs = [f"J{i}" for i in range(1, 13)]
    machines = ["M1", "M2", "M3"]

    processing_time = {
        "J1": 14,
        "J2": 9,
        "J3": 18,
        "J4": 7,
        "J5": 13,
        "J6": 6,
        "J7": 11,
        "J8": 16,
        "J9": 8,
        "J10": 10,
        "J11": 15,
        "J12": 5,
    }

    return SchedulingData(
        jobs=jobs,
        machines=machines,
        processing_time=processing_time,
    )


def build_model(data: SchedulingData) -> Tuple[
    pulp.LpProblem,
    Dict[Tuple[str, str], pulp.LpVariable],
    pulp.LpVariable,
]:
    """Build the MILP model.

    Decision variable
    -----------------
    x[j, m] = 1 if job j is assigned to machine m; 0 otherwise.

    Makespan variable
    -----------------
    c_max represents the maximum machine workload.

    Objective
    ---------
    Minimize c_max.

    Constraints
    -----------
    1. Every job is assigned to exactly one machine.
    2. The workload of every machine is at most c_max.
    """

    model = pulp.LpProblem("Parallel_Machine_Scheduling", pulp.LpMinimize)

    x = pulp.LpVariable.dicts(
        "assign",
        [(j, m) for j in data.jobs for m in data.machines],
        lowBound=0,
        upBound=1,
        cat=pulp.LpBinary,
    )

    c_max = pulp.LpVariable("makespan", lowBound=0, cat=pulp.LpContinuous)

    model += c_max, "Minimize_Makespan"

    for job in data.jobs:
        model += (
            pulp.lpSum(x[(job, machine)] for machine in data.machines) == 1,
            f"Assign_{job}_Once",
        )

    for machine in data.machines:
        model += (
            pulp.lpSum(
                data.processing_time[job] * x[(job, machine)]
                for job in data.jobs
            )
            <= c_max,
            f"Makespan_Bound_{machine}",
        )

    return model, x, c_max


def solve_model(model: pulp.LpProblem) -> None:
    """Solve the model with CBC, which is distributed with PuLP."""

    solver = pulp.PULP_CBC_CMD(msg=False)
    model.solve(solver)

    if pulp.LpStatus[model.status] != "Optimal":
        raise RuntimeError(
            f"Solver did not find an optimal solution. Status: "
            f"{pulp.LpStatus[model.status]}"
        )


def extract_schedule(
    data: SchedulingData,
    x: Dict[Tuple[str, str], pulp.LpVariable],
) -> Dict[str, List[str]]:
    """Return the jobs assigned to each machine.

    Jobs are ordered by decreasing processing time only for reporting purposes.
    For identical parallel machines with no release dates or sequence-dependent
    effects, the within-machine order does not change the makespan.
    """

    schedule: Dict[str, List[str]] = {machine: [] for machine in data.machines}

    for machine in data.machines:
        assigned_jobs = [
            job
            for job in data.jobs
            if pulp.value(x[(job, machine)]) is not None
            and pulp.value(x[(job, machine)]) > 0.5
        ]
        schedule[machine] = sorted(
            assigned_jobs,
            key=lambda job: data.processing_time[job],
            reverse=True,
        )

    return schedule


def print_solution(
    data: SchedulingData,
    schedule: Dict[str, List[str]],
    c_max: pulp.LpVariable,
) -> None:
    """Print the optimized schedule and machine workloads."""

    print("Parallel Machine Scheduling - MILP Optimization")
    print("=" * 48)
    print(f"Optimal makespan: {pulp.value(c_max):.0f}\n")

    for machine in data.machines:
        jobs = schedule[machine]
        load = sum(data.processing_time[job] for job in jobs)

        print(f"{machine} | total load = {load}")
        for job in jobs:
            print(f"  - {job}: {data.processing_time[job]} time units")
        print()


def main() -> None:
    """Run the complete optimization workflow."""

    data = build_sample_data()
    model, x, c_max = build_model(data)
    solve_model(model)
    schedule = extract_schedule(data, x)
    print_solution(data, schedule, c_max)


if __name__ == "__main__":
    main()
