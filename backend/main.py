import os
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from redis import Redis
from rq import Queue
from rq.job import Job
from rq.exceptions import NoSuchJobError
from typing import Literal

app=FastAPI(title="Hybrid HPC API")
def connection():
    return Redis.from_url(os.getenv("REDIS_URL","redis://localhost:6379/0"))

class Workload(BaseModel):
    kind: Literal["matrix","quantum"]
    size: int=Field(ge=1,le=2048)

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/jobs",status_code=202)
def submit(workload: Workload):
    if workload.kind=="quantum" and not 2<=workload.size<=20:
        raise HTTPException(422,"Invalid qubit count")
    job=Queue(connection=connection()).enqueue("backend.worker.execute_job",workload.kind,workload.size,job_id=str(uuid.uuid4()),job_timeout=120,result_ttl=86400)
    return {"id":job.id}

@app.get("/jobs/{job_id}")
def status(job_id: str):
    try:
        job=Job.fetch(job_id,connection=connection())
    except NoSuchJobError:
        raise HTTPException(404,"Job not found")
    return {"id":job.id,"status":job.get_status().value,"result":job.result}
