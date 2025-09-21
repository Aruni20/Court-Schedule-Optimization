# Automated Court Scheduling & Optimization: A Real-Time, MILP-Driven Pipeline to Combat Case Backlog  
**Solving the Timely Justice Paradox with Event-Driven Data and Mathematical Optimization**

---

## Introduction  
The Indian judicial system is grappling with an overwhelming backlog exceeding **5 crore cases**, primarily due to a **static and fragmented scheduling process**. Existing systems fail to adapt to dynamic changes like judge transfers, lawyer availability, or real-time urgency of cases.  

This project proposes a **hybrid pipeline** that merges **real-time event intelligence** with **Mixed-Integer Linear Programming (MILP)** to generate efficient, fair, and adaptive court schedules.

---

## Overview  
**Core Question:**  
Can we drastically reduce judicial backlog by creating an end-to-end, automated system that maintains a **real-time dataset** and uses a **nightly MILP solver** to produce an optimal schedule?  

Our work introduces a **two-stage data pipeline**:  
1. **Event-driven ETL architecture** ensuring continuous data freshness.  
2. **Batch ELT optimization engine** using MILP for globally optimal scheduling.  

This design replaces **static heuristics** with **dynamic optimization**, ensuring fairness and efficiency in judicial scheduling.

---

## Motivation  

### Flawed Assumptions in Traditional Systems  
- A central database is always up-to-date.  
- Events (filings, transfers) can be handled linearly.  
- Schedules can be built with simple heuristics.  

### Reality  
- No **single source of truth** for events.  
- **Stale inputs** → suboptimal schedules.  
- Scheduling is a **complex optimization problem** with constraints (judge specialization, case urgency, lawyer conflicts).  

**Result:** Inefficiency → growing backlog → delayed justice.  

**Our Solution:** Event-driven data + MILP optimization.
---
**System Architecture:** 


The architecture is divided into two layers:

1. **Nayaya Stream (Operational ETL & Batch Optimization)**  
   - **FAKER** generates synthetic case data.  
   - Data flows through **Kafka** (message bus) into the **Real-Time Scoring Consumer**, which ingests, scores, and stores cases.  
   - Results are updated into the **MySSOL database**, which maintains pending cases.  
   - A **nightly trigger** schedules cases based on scoring and optimization.  

2. **NitiView (Analytical ELT & Monitoring, Weekly)**  
   - Historical and batch data are stored in **MinIO (Data Lake)**.  
   - An **Analytics Engine** performs ETL (Extract, Load, Transform) for weekly insights.  
   - Results are visualized in the **Streamlit Dashboard**, providing interactive monitoring and reports.  

This hybrid design ensures that **Nayaya Stream handles real-time case scheduling** while **NitiView provides long-term analytical monitoring**, enabling fair and efficient court scheduling.

---

<img width="565" height="555" alt="Image" src="https://github.com/user-attachments/assets/97bd66c0-64cd-4dfe-8ba3-9329efdc0207" />


## Core Components & Mathematical Formulation  

### Component 1: Real-Time Event Bus (ETL Pipeline)  
**Problem:** Static databases cannot reflect real-world dynamics quickly enough.  

**Solution:**  
- **Kafka Producer** streams all events (`case_filed`, `lawyer_transfer`, `judge_assigned`).  
- **Kafka Consumer** applies transformations (priority scoring, filtering) and updates the **MySQL master database**.  
- Ensures **continuous freshness** of input data.  

**Impact:** MySQL becomes the **authoritative single source of truth**.

---

### Component 2: Batch Optimization Engine (ELT Pipeline)  
**Problem:** Scheduling is an NP-hard optimization problem, not solvable by heuristics.  

**Solution:**  
- **Airflow DAG** triggers nightly Python MILP solver (using PuLP/SciPy).  
- Extracts **latest data** from MySQL.  
- Solves **MILP model**.  
- Exports optimized schedule to **MinIO** for operational use.  

---
## Mathematical Formulation


**Sets:**
- \( C \): Pending cases  
- \( J \): Judges  
- \( T \): Time slots  

## Parameters

- $p_c$: Priority score of case $c$  
- $d_c$: Duration of case $c$ (in slots)  
- $a_{jc}$: Judge $j$ authorized for case $c$ (binary)  

## Decision Variable

- $x_{cjt} \in \{0,1\}$: 1 if case $c$ is assigned to judge $j$ at time $t$, else 0  

---

### Objective Function
Maximize the total weighted priority of scheduled cases:

$$
\text{Maximize } Z = \sum_{c \in C} \sum_{j \in J} \sum_{t \in T} p_c \cdot x_{cjt}
$$

---

### Constraints

1. **Each case scheduled at most once:**

$$
\sum_{j \in J} \sum_{t \in T} x_{cjt} \leq 1 \quad \forall c \in C
$$

2. **Judge handles only one case per slot:**

$$
\sum_{c \in C} x_{cjt} \leq 1 \quad \forall j \in J, \forall t \in T
$$

3. **Case duration fits within slot:**

$$
d_c \cdot x_{cjt} \leq 1 \quad \forall c \in C, \forall j \in J, \forall t \in T
$$

4. **Judge-case authorization:**

$$
x_{cjt} \leq a_{jc} \quad \forall c \in C, \forall j \in J, \forall t \in T
$$

---

## Expected Results & Impact  

| Metric              | Current System (Heuristics) | Our Solution (MILP) | Expected Improvement |
|----------------------|------------------------------|----------------------|-----------------------|
| Schedule Efficiency | Sub-optimal                 | Optimal              | Drastic increase in cases heard per judge |
| Backlog Reduction   | Stagnant                    | Accelerated          | >20% reduction per year possible |
| Data Freshness      | Stale                       | Real-Time            | Always up-to-date schedules |
| Fairness            | Heuristic-driven            | Optimized variables  | Fairness constraints integrated |

---

## Operational Impact
- Judges, clerks, and lawyers receive **fair, predictable, real-time schedules**.  

## Analytical Impact
- Policy analysts can **audit efficiency**, backlog reduction, and fairness outcomes.  

---

## Keywords
Mixed-Integer Linear Programming (MILP), Real-Time Data Pipeline, Event-Driven Architecture, Judicial Reform, Resource Optimization, Apache Airflow, Apache Kafka, Data Engineering, Case Backlog

