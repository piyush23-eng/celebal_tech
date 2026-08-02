# TransactShield

Real-time transaction fraud detection platform — synthetic data pipeline, a two-layer ML risk model, a scoring API with live WebSocket streaming, and a live risk-ops dashboard.

## Why this project

Fintech and payments companies (Razorpay, PhonePe, JusPay, and similar) run exactly this kind of system in production: transactions flow in, get scored for risk in milliseconds, and get surfaced to an ops/fraud team with an explanation, not just a number. This project reproduces that pipeline end to end at a portfolio scale.

## Architecture

```
generate_transactions.py          train_model.py                 main.py (FastAPI)                index.html
   (synthetic UPI/card    ---->  IsolationForest (unsupervised) --->  /score  (REST)      <---->  live ledger
    transactions with            + XGBoost (supervised) blended        /ws/live (WebSocket)          risk trend chart
    5 injected fraud              into a 0-100 risk score               rule-based explanation        alerts panel
    patterns, labeled)                                                   layer per transaction
```

- **Data layer**: `data/generate_transactions.py` — 500 synthetic users, ~20k transactions, 5 realistic fraud patterns injected (impossible travel, velocity abuse, odd-hour spikes, new-device + high value, merchant testing/card-testing).
- **ML layer**: `ml/train_model.py` — feature engineering (distance from home city via haversine, spend-ratio vs personal baseline, device recognition, transaction velocity, odd-hour flag), then an IsolationForest (catches novel fraud patterns without labels) blended with an XGBoost classifier (precise on known patterns). Achieves ROC-AUC ~0.97 / Average Precision ~0.93 on held-out data.
- **Serving layer**: `backend/main.py` — FastAPI app. `POST /score` scores a single transaction; `WS /ws/live` streams a simulated live feed, each transaction pre-scored with a plain-English explanation of why it was flagged.
- **UI layer**: `frontend/index.html` — a single self-contained dashboard (no build step). Connects to the live backend over WebSocket; if no backend is running, it automatically falls back to an in-browser simulation so the demo always works standalone.

## Running it

```bash
# 1. Generate data + train the model
cd data && python3 generate_transactions.py
cd ../ml && python3 train_model.py

# 2. Start the API
cd ../backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# 3. Open the dashboard
# just open frontend/index.html directly in a browser — it will
# connect to ws://localhost:8000/ws/live automatically
```

No backend running? Open `frontend/index.html` on its own — it detects the missing connection in ~2.5s and switches to a self-contained demo simulation, so you can always show this project even without spinning up Python.

## Scaling this further (talk about this in interviews)

- Swap the in-memory `random_live_transaction()` simulator for a real Kafka topic; FastAPI's WebSocket handler becomes a Kafka consumer.
- Move `user_state` (currently in-process dict) to Redis so the scoring service can run as multiple stateless replicas behind a load balancer.
- Batch-retrain the XGBoost model on a schedule (Airflow/ADF) as fraud patterns drift — you already have this exact experience from your Celebal ADF pipeline work.
- Containerize `backend/` with Docker, deploy on Azure Container Apps or AKS for a horizontal-scale story.
- Swap `rule_based_explain()` in `backend/main.py` for a real Claude API call (stubbed function `llm_explain()` is already there) to get generative, more nuanced fraud explanations for analysts.

## Resume bullet (starting point — edit to your voice)

> Built TransactShield, a real-time transaction fraud detection platform: engineered a synthetic transaction pipeline with 5 realistic fraud patterns, trained a blended IsolationForest + XGBoost risk model (ROC-AUC 0.97), and served real-time risk scores via a FastAPI WebSocket API to a live monitoring dashboard — architected with a clear path to Kafka/Redis/AKS for horizontal scale.

## Project structure

```
transactshield/
├── data/
│   └── generate_transactions.py
├── ml/
│   ├── train_model.py
│   ├── scaler.joblib
│   ├── isolation_forest.joblib
│   ├── xgb_model.joblib
│   ├── feature_cols.json
│   └── metrics.json
├── backend/
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   └── index.html
└── README.md
```
