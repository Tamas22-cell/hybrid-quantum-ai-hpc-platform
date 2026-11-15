"""Password and server-side session management for the public HPC dashboard."""

from __future__ import annotations

import hashlib
import hmac
import os
import re
import secrets
import base64
from dataclasses import dataclass
from typing import Annotated

import psycopg
from fastapi import Cookie, Header, HTTPException, Request
from psycopg.errors import UniqueViolation
from redis import Redis
from redis.exceptions import RedisError

SESSION_COOKIE = "hpc_session"
SESSION_TTL_SECONDS = 60 * 60 * 24 * 7
EMAIL_RE = re.compile(r"^[^\s@]{1,64}@[^\s@.]+(?:\.[^\s@.]+)+$")


@dataclass(frozen=True)
class UserIdentity:
    id: str
    email: str


def database_connection():
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        raise HTTPException(status_code=503, detail="Database unavailable")
    return psycopg.connect(dsn, connect_timeout=5)


def ensure_schema() -> None:
    """Create auth tables and add an owner column without exposing legacy rows."""
    try:
        with database_connection() as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS hpc_users (
                    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
                    email text NOT NULL UNIQUE,
                    password_hash text NOT NULL,
                    created_at timestamptz NOT NULL DEFAULT now()
                )"""
            )
            conn.execute(
                """CREATE TABLE IF NOT EXISTS hpc_sessions (
                    token_hash text PRIMARY KEY,
                    user_id uuid NOT NULL REFERENCES hpc_users(id) ON DELETE CASCADE,
                    expires_at timestamptz NOT NULL,
                    created_at timestamptz NOT NULL DEFAULT now()
                )"""
            )
            conn.execute(
                """CREATE TABLE IF NOT EXISTS results (
                    id text PRIMARY KEY,
                    payload jsonb NOT NULL,
                    created_at timestamptz
                )"""
            )
            conn.execute("ALTER TABLE results ADD COLUMN IF NOT EXISTS created_at timestamptz")
            conn.execute(
                """ALTER TABLE results ADD COLUMN IF NOT EXISTS user_id uuid
                   REFERENCES hpc_users(id) ON DELETE CASCADE"""
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS results_user_created_idx "
                "ON results (user_id, created_at DESC NULLS LAST)"
            )
            conn.execute("DELETE FROM hpc_sessions WHERE expires_at <= now()")
    except HTTPException:
        raise
    except psycopg.Error:
        raise HTTPException(status_code=503, detail="Database unavailable") from None


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    derived = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=64)
    salt_text = base64.urlsafe_b64encode(salt).decode("ascii")
    hash_text = base64.urlsafe_b64encode(derived).decode("ascii")
    return f"scrypt$16384$8$1${salt_text}${hash_text}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algorithm, n, r, p, salt_text, hash_text = stored.split("$", 5)
        if algorithm != "scrypt":
            return False
        salt = base64.urlsafe_b64decode(salt_text.encode("ascii"))
        expected = base64.urlsafe_b64decode(hash_text.encode("ascii"))
        actual = hashlib.scrypt(
            password.encode("utf-8"), salt=salt, n=int(n), r=int(r), p=int(p), dklen=len(expected)
        )
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError, UnicodeError):
        return False


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("ascii")).hexdigest()


def _rate_limit(key: str, limit: int, window_seconds: int) -> None:
    try:
        redis = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), socket_connect_timeout=3)
        count = redis.eval(
            "local n=redis.call('INCR',KEYS[1]); "
            "if n==1 then redis.call('EXPIRE',KEYS[1],ARGV[1]) end; return n",
            1,
            key,
            window_seconds,
        )
    except (RedisError, ValueError):
        raise HTTPException(status_code=503, detail="Authentication service unavailable") from None
    if count > limit:
        raise HTTPException(status_code=429, detail="Too many attempts", headers={"Retry-After": str(window_seconds)})


def _client_key(request: Request) -> str:
    client_ip = request.headers.get("x-client-ip", "").strip()
    if not client_ip:
        forwarded = request.headers.get("x-forwarded-for", "")
        client_ip = forwarded.split(",", 1)[0].strip() or (request.client.host if request.client else "unknown")
    return hashlib.sha256(client_ip.encode("utf-8")).hexdigest()[:32]


def authorize_internal(x_api_key: str = Header(default="")) -> None:
    secret = os.getenv("HPC_API_KEY", "")
    if not secret:
        raise HTTPException(status_code=503, detail="Authentication service unavailable")
    if not hmac.compare_digest(secret.encode("utf-8"), x_api_key.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Unauthorized")


def register_user(email: str, password: str) -> tuple[str, UserIdentity]:
    normalized_email = email.strip().lower()
    if not EMAIL_RE.fullmatch(normalized_email) or len(normalized_email) > 254:
        raise HTTPException(status_code=422, detail="Enter a valid email address")
    if not 12 <= len(password) <= 128:
        raise HTTPException(status_code=422, detail="Password must be 12–128 characters")

    token = secrets.token_urlsafe(32)
    try:
        with database_connection() as conn:
            row = conn.execute(
                "INSERT INTO hpc_users (email, password_hash) VALUES (%s, %s) RETURNING id::text, email",
                (normalized_email, hash_password(password)),
            ).fetchone()
            conn.execute(
                "INSERT INTO hpc_sessions (token_hash, user_id, expires_at) VALUES (%s, %s, now() + (%s * interval '1 second'))",
                (_token_hash(token), row[0], SESSION_TTL_SECONDS),
            )
        return token, UserIdentity(id=row[0], email=row[1])
    except UniqueViolation:
        raise HTTPException(status_code=409, detail="An account with this email already exists") from None
    except HTTPException:
        raise
    except psycopg.Error:
        raise HTTPException(status_code=503, detail="Account service unavailable") from None


def login_user(email: str, password: str) -> tuple[str, UserIdentity]:
    normalized_email = email.strip().lower()
    try:
        with database_connection() as conn:
            row = conn.execute(
                "SELECT id::text, email, password_hash FROM hpc_users WHERE email = %s",
                (normalized_email,),
            ).fetchone()
            if row is None:
                verify_password(password, _DUMMY_PASSWORD_HASH)
                raise HTTPException(status_code=401, detail="Invalid email or password")
            if not verify_password(password, row[2]):
                raise HTTPException(status_code=401, detail="Invalid email or password")
            token = secrets.token_urlsafe(32)
            conn.execute(
                "INSERT INTO hpc_sessions (token_hash, user_id, expires_at) VALUES (%s, %s, now() + (%s * interval '1 second'))",
                (_token_hash(token), row[0], SESSION_TTL_SECONDS),
            )
        return token, UserIdentity(id=row[0], email=row[1])
    except HTTPException:
        raise
    except psycopg.Error:
        raise HTTPException(status_code=503, detail="Account service unavailable") from None


_DUMMY_PASSWORD_HASH = hash_password(secrets.token_urlsafe(32))


def require_auth_attempt(request: Request, action: str) -> None:
    limit, window = (3, 3600) if action == "register" else (8, 300)
    _rate_limit(f"hpc:auth:{action}:{_client_key(request)}", limit, window)


def revoke_session(token: str | None) -> None:
    if not token:
        return
    try:
        with database_connection() as conn:
            conn.execute("DELETE FROM hpc_sessions WHERE token_hash = %s", (_token_hash(token),))
    except HTTPException:
        raise
    except psycopg.Error:
        raise HTTPException(status_code=503, detail="Could not revoke session") from None


def current_user(session: Annotated[str | None, Cookie(alias=SESSION_COOKIE)] = None) -> UserIdentity:
    if not session:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        with database_connection() as conn:
            row = conn.execute(
                """SELECT u.id::text, u.email FROM hpc_sessions s
                   JOIN hpc_users u ON u.id = s.user_id
                   WHERE s.token_hash = %s AND s.expires_at > now()""",
                (_token_hash(session),),
            ).fetchone()
    except (HTTPException, psycopg.Error):
        raise HTTPException(status_code=503, detail="Authentication service unavailable") from None
    if row is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    return UserIdentity(id=row[0], email=row[1])


def limit_workload(user_id: str) -> None:
    try:
        redis = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), socket_connect_timeout=3)
        count = redis.eval(
            "local n=redis.call('INCR',KEYS[1]); "
            "if n==1 then redis.call('EXPIRE',KEYS[1],60) end; return n",
            1,
            f"hpc:submission_limit:{user_id}",
        )
    except (RedisError, ValueError):
        raise HTTPException(status_code=503, detail="Queue unavailable") from None
    if count > 10:
        raise HTTPException(status_code=429, detail="Submission rate exceeded", headers={"Retry-After": "60"})
