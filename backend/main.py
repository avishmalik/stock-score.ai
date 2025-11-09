from fastapi import FastAPI
from datetime import datetime
from backend.workers.scheduler import run_hourly_batch

app = FastAPI(title="Stock Score AI")

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/run-hourly")
def run_hourly_now():
    run_hourly_batch(datetime.now())
    return {"status": "queued", "time": datetime.now().isoformat()}
