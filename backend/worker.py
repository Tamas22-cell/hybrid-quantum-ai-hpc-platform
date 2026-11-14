import os
import psycopg
from psycopg.types.json import Jsonb
from rq import get_current_job
from ai_agents.orchestrator import execute

def execute_job(kind,size):
    result=execute(kind,size)
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS results (id text PRIMARY KEY, payload jsonb NOT NULL)")
        conn.execute("INSERT INTO results VALUES (%s,%s) ON CONFLICT (id) DO UPDATE SET payload=EXCLUDED.payload",(get_current_job().id,Jsonb(result)))
    return result
