# RidePulse — Bike Rental Demand Prediction

A FastAPI web application that predicts hourly bike-rental demand with the existing tuned LightGBM model.

## Run locally

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open `http://127.0.0.1:8000`.

API documentation is available at `http://127.0.0.1:8000/docs`.

## API

- `GET /api/health` — health check
- `POST /api/predict` — generate a bike-rental demand prediction

## Deploy on Render

1. Push this project to a GitHub repository.
2. In Render choose **New + → Blueprint** and connect the repository.
3. Render detects `render.yaml` automatically.
4. Deploy. The included health endpoint is `/api/health`.

You can also create a normal Web Service with:

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## Docker

```bash
docker build -t ridepulse .
docker run -p 8000:8000 ridepulse
```
