from fastapi import FastAPI
from uuid import uuid4

app = FastAPI(title="Mock FCC API", version="1.0.0")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/fcc/robocall")
async def submit_robocall():
    return {"state": "submitted", "reference": str(uuid4())}
