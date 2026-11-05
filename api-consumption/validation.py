from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
checks = []

print("\n")

def check(label, response, expected):
    ok = response.status_code == expected

    print(f"[{'PASS' if ok else 'FAIL'}]: {label}: HTTP {response.status_code} (expected {expected})")
    checks.append(ok)
    return response

check("Home Page Check", client.get("/"),200)
check("Home Page Check", client.get("/products"),200)