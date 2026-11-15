import os
import psycopg
from psycopg.types.json import Jsonb
from rq import get_current_job
from ai_agents.orchestrator import execute
from backend.security import ensure_schema

def execute_job(kind,size):
    job = get_current_job()
    if job is None or not job.meta.get("owner_id"):
        raise ValueError("Workload owner is missing")
    ensure_schema()
    result=execute(kind,size)
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        conn.execute(
            """INSERT INTO results (id,payload,created_at,user_id) VALUES (%s,%s,now(),%s)
               ON CONFLICT (id) DO UPDATE SET payload=EXCLUDED.payload,
               created_at=EXCLUDED.created_at,user_id=EXCLUDED.user_id""",
            (job.id, Jsonb(result), job.meta["owner_id"]),
        )
    return result
