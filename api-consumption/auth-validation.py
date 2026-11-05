#!/usr/bin/env python3
import os
import sys
from datetime import datetime, timezone
import httpx
import jwt

BASE = "http://127.0.0.1:8000"
USERNAME = os.getenv("DEMO_USERNAME")
PASSWORD = os.getenv("DEMO_PASSWORD")
SECRET = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"

if not USERNAME or not PASSWORD or not SECRET:
    print("[FAIL] Required training environment variables are not set.")
    sys.exit(2)

passed = failed = 0

def check(label, ok, detail=""):
    global passed, failed
    print(f"[{'PASS' if ok else 'FAIL'}] {label} {detail}")
    passed += int(bool(ok))
    failed += int(not ok)


with httpx.Client(base_url=BASE, timeout=5.0) as client:
    r = client.get("/products")
    check("Public GET /products", r.status_code == 200, f"HTTP {r.status_code}")

    payload = {"name":"printer", "price": 45534, "in_stock": True}
    r = client.post("/products", json=payload)
    check("POST /products without token -> 401", r.status_code == 401, f"HTTP {r.status_code}")

    r = client.post("/auth/token", data={"username": USERNAME, "password": PASSWORD})
    check("Valid login -> 200", r.status_code == 200, f"HTTP {r.status_code}")
    # Get the token from valid login
    token = r.json().get("access_token") if r.status_code == 200 else None
    check("Valid login -> bearer token", r.status_code == 200 and bool(token), f"HTTP {r.status_code}")

    payload = {"name":"printer", "price": 45534, "in_stock": True}
    r = client.post("/products", json=payload, headers={"Authorization": f"Bearer {token}"})
    check("Authenticated POST /products -> 201", r.status_code == 201, f"HTTP {r.status_code}")


