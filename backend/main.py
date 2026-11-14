import os
import uuid
import time
import logging
from prometheus_client import Counter, Histogram, make_asgi_app
from backend.security import authorize, limit
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from redis import Redis
from rq import Queue
from rq.job import Job
from rq.exceptions import NoSuchJobError
from typing import Literal

app=FastAPI(title="Hybrid HPC API")
requests=Counter("hpc_http_requests","HTTP requests",["method","status"])
duration=Histogram("hpc_http_duration_seconds","HTTP duration")
app.mount("/metrics",make_asgi_app())
@app.middleware("http")
async def observe(request,call_next):
    start=time.perf_counter()
    response=await call_next(request)
    requests.labels(request.method,response.status_code).inc()
    duration.observe(time.perf_counter()-start)
    logging.getLogger("uvicorn.error").info("method=%s status=%s",request.method,response.status_code)
    return response

def connection():
    return Redis.from_url(os.getenv("REDIS_URL","redis://localhost:6379/0"))

class Workload(BaseModel):
    kind: Literal["matrix","quantum"]
    size: int=Field(ge=1,le=2048)

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/jobs",status_code=202,dependencies=[Depends(authorize),Depends(limit)])
def submit(workload: Workload):
    if workload.kind=="quantum" and not 2<=workload.size<=20:
        raise HTTPException(422,"Invalid qubit count")
    job=Queue(connection=connection()).enqueue("backend.worker.execute_job",workload.kind,workload.size,job_id=str(uuid.uuid4()),job_timeout=120,result_ttl=86400)
    return {"id":job.id}

@app.get("/jobs/{job_id}",dependencies=[Depends(authorize)])
def status(job_id: str):
    try:
        job=Job.fetch(job_id,connection=connection())
    except NoSuchJobError:
        raise HTTPException(404,"Job not found")
    return {"id":job.id,"status":job.get_status().value,"result":job.result}
