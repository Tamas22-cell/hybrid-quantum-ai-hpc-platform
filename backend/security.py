import os
import hmac
from fastapi import Header, HTTPException
from redis import Redis
from redis.exceptions import RedisError

def authorize(x_api_key: str = Header(default="")):
    secret=os.getenv("HPC_API_KEY","")
    if not secret:
        raise HTTPException(503,"Authentication not configured")
    if not hmac.compare_digest(secret.encode(),x_api_key.encode()):
        raise HTTPException(401,"Unauthorized")

def limit():
    try:
        redis=Redis.from_url(os.getenv("REDIS_URL","redis://localhost:6379/0"))
        count=redis.eval("local n=redis.call('INCR',KEYS[1]); if n==1 then redis.call('EXPIRE',KEYS[1],60) end; return n",1,"hpc:submission_limit")
    except RedisError:
        raise HTTPException(503,"Queue unavailable")
    if count>10:
        raise HTTPException(429,"Submission rate exceeded",headers={"Retry-After":"60"})
