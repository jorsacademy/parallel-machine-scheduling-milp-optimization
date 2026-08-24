# Parallel Machine Scheduling with MILP Optimization

This project demonstrates a medium-level **identical parallel machine scheduling** problem solved with a **Mixed-Integer Linear Programming (MILP)** model in Python.

The goal is to assign a set of independent jobs to parallel machines so that the **makespan** — the maximum workload assigned to any machine — is minimized.

## Problem Description

We consider:

- 12 independent jobs
- 3 identical parallel machines
- A deterministic processing time for each job
- No preemption
- No release dates
- No sequence-dependent setup times

Each job must be assigned to exactly one machine.

Because the machines are identical and there are no sequence-dependent effects, the internal ordering of jobs on a machine does not affect the makespan. Therefore, the optimization model focuses on the assignment decision.

## Mathematical Formulation

### Sets

- `J`: set of jobs
- `M`: set of machines

### Parameter

- `p_j`: processing time of job `j`

### Decision Variable

- `x_jm = 1` if job `j` is assigned to machine `m`, and `0` otherwise

### Makespan Variable

- `C_max`: maximum workload among all machines

### Objective Function

Minimize:

```text
C_max
```

### Constraints

Each job must be assigned exactly once:

```text
sum_m x_jm = 1    for every job j
```

The workload of every machine must not exceed the makespan:

```text
sum_j p_j * x_jm <= C_max    for every machine m
```

Binary restrictions:

```text
x_jm in {0, 1}
```

## Sample Data

| Job | Processing Time |
|---|---:|
| J1 | 14 |
| J2 | 9 |
| J3 | 18 |
| J4 | 7 |
| J5 | 13 |
| J6 | 6 |
| J7 | 11 |
| J8 | 16 |
| J9 | 8 |
| J10 | 10 |
| J11 | 15 |
| J12 | 5 |

## Technologies

- Python 3.10+
- PuLP
- CBC MILP Solver

## Installation

Clone the repository and install the dependency:

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

The program prints:

- Solver status validation
- Optimal makespan
- Job assignments for each machine
- Total workload of each machine

## Why This Formulation Is Correct

A common modeling mistake is to introduce completion-time variables indexed by sequence positions without also defining valid sequencing constraints. That creates variables that do not correspond to an actual schedule.

This project avoids that error. For the identical parallel machine problem considered here, minimizing the largest machine workload is sufficient to minimize the makespan. The MILP therefore uses only job-to-machine assignment variables and one makespan variable.

## Project Structure

```text
.
├── main.py
├── README.md
├── requirements.txt
├── .gitignore
└── LICENSE
```

## License

This repository is **not licensed for commercial use**.

The source code may be used for personal, educational, and non-commercial research purposes only. Commercial use, commercial redistribution, sublicensing, resale, or incorporation into a commercial product or service requires prior written permission from the copyright holder.

See the `LICENSE` file for the complete terms.
