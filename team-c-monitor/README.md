# Team C – Real-Time AI API Monitoring & Anomaly Detection

This project is a FastAPI + Streamlit based system that monitors AI API usage in real time, computes rolling metrics, and detects anomalies using streaming data.

## Problem Statement

Modern AI APIs must be continuously monitored to ensure reliability, detect failures, and prevent abuse.  
This project simulates a real-time monitoring system that ingests API logs and detects abnormal behavior such as latency spikes, error spikes, and unusual per-user usage.

## Learning Objectives

- Apply data structures and algorithms in real-world systems
- Build REST APIs using FastAPI
- Create an interactive dashboard using Streamlit
- Implement sliding window metrics on streaming data
- Follow professional Git workflows

## System Architecture

- Backend: FastAPI for ingesting logs and exposing metrics
- Core Logic: Sliding window, metrics calculation, anomaly detection
- Frontend: Streamlit dashboard for visualization

## Core Data Structures & Algorithms

- Sliding Window using deque
- Hash maps for aggregating metrics
- Mean and standard deviation for anomaly detection

## Anomaly Detection

Baseline metrics are calculated over a sliding time window.

An anomaly is detected when:
mean + k × standard deviation is exceeded

Severity levels:

- HEALTHY
- WARNING
- CRITICAL

## How to Run

Install dependencies:

```bash
pip install -r requirements.txt
```

## How to Run & Test

Run backend:

```bash
cd team-c-monitor
uvicorn backend.app.main:app --reload

```

Run Frontend

```bash
cd team-c-monitor/frontend
streamlit run app.py
```

Run unit tests:

```bash
cd team-c-monitor/test
pytest
```
