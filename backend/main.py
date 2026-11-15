import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import Cookie, Depends, FastAPI, HTTPException, Request
from prometheus_client import Counter, Histogram, make_asgi_app
from pydantic import BaseModel, Field
from redis import Redis
from redis.exceptions import RedisError
from rq import Queue
from rq.exceptions import NoSuchJobError
from rq.job import Job

from backend.security import (
    SESSION_COOKIE,
    UserIdentity,
    authorize_internal,
    current_user,
    ensure_schema,
    limit_workload,
    login_user,
    register_user,
    require_auth_attempt,
    revoke_session,
)

@asynccontextmanager
async def lifespan(_app):
    ensure_schema()
    yield


app = FastAPI(title="Hybrid HPC API", lifespan=lifespan)
requests = Counter("hpc_http_requests", "HTTP requests", ["method", "status"])
duration = Histogram("hpc_http_duration_seconds", "HTTP duration")
app.mount("/metrics", make_asgi_app())


@app.middleware("http")
async def observe(request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    requests.labels(request.method, response.status_code).inc()
    duration.observe(time.perf_counter() - start)
    logging.getLogger("uvicorn.error").info("method=%s status=%s", request.method, response.status_code)
    return response


def connection():
    return Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))


class Workload(BaseModel):
    kind: Literal["matrix", "quantum"]
    size: int = Field(ge=1, le=2048)


class Credentials(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=128)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/register", status_code=201, dependencies=[Depends(authorize_internal)])
def register(data: Credentials, request: Request):
    require_auth_attempt(request, "register")
    token, user = register_user(data.email, data.password)
    return {"session_token": token, "user": {"id": user.id, "email": user.email}}


@app.post("/auth/login", dependencies=[Depends(authorize_internal)])
def login(data: Credentials, request: Request):
    require_auth_attempt(request, "login")
    token, user = login_user(data.email, data.password)
    return {"session_token": token, "user": {"id": user.id, "email": user.email}}


@app.get("/auth/me")
def me(user: UserIdentity = Depends(current_user)):
    return {"id": user.id, "email": user.email}


@app.post("/auth/logout")
def logout(session: str | None = Cookie(default=None, alias=SESSION_COOKIE)):
    revoke_session(session)
    return {"ok": True}


@app.post("/jobs", status_code=202)
def submit(workload: Workload, user: UserIdentity = Depends(current_user)):
    if workload.kind == "quantum" and not 2 <= workload.size <= 20:
        raise HTTPException(422, "Invalid qubit count")
    limit_workload(user.id)
    job = Queue(connection=connection()).enqueue(
        "backend.worker.execute_job",
        workload.kind,
        workload.size,
        job_id=str(uuid.uuid4()),
        job_timeout=120,
        result_ttl=86400,
        meta={"owner_id": user.id},
    )
    return {"id": job.id}


@app.get("/jobs/{job_id}")
def status(job_id: str, user: UserIdentity = Depends(current_user)):
    try:
        job = Job.fetch(job_id, connection=connection())
    except NoSuchJobError:
        raise HTTPException(404, "Job not found") from None
    if job.meta.get("owner_id") != user.id:
        raise HTTPException(404, "Job not found")
    return {"id": job.id, "status": job.get_status().value, "result": job.result}


@app.get("/history")
def history(user: UserIdentity = Depends(current_user)):
    import os

    import psycopg

    try:
        with psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=5) as conn:
            rows = conn.execute(
                """SELECT id, payload, created_at FROM results
                   WHERE user_id = %s ORDER BY created_at DESC NULLS LAST, id LIMIT 100""",
                (user.id,),
            ).fetchall()
        return {
            "items": [
                {"id": row[0], "payload": row[1], "created_at": row[2]}
                for row in rows
            ]
        }
    except (psycopg.Error, KeyError):
        raise HTTPException(503, "History unavailable") from None


@app.get("/system-status")
def system_status(user: UserIdentity = Depends(current_user)):
    import os

    import psycopg
    from rq import Worker

    checks = {"api": "online", "redis": "unavailable", "database": "unavailable", "worker": "unknown"}
    try:
        redis = Redis.from_url(os.environ["REDIS_URL"], socket_connect_timeout=3, socket_timeout=3)
        if redis.ping():
            checks["redis"] = "online"
            checks["worker"] = "registered" if Worker.count(connection=redis) else "not registered"
    except (RedisError, KeyError, ValueError):
        pass
    try:
        with psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=3) as conn:
            conn.execute("SELECT 1").fetchone()
        checks["database"] = "online"
    except (psycopg.Error, KeyError):
        pass
    return checks
