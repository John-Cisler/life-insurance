import json

def test_create_and_get(client):
    payload = {"customerId": 101, "coverage": 100000, "annualPremium": 300.0}
    r = client.post("/policies", json=payload)
    assert r.status_code == 201
    pid = r.get_json()["id"]

    r2 = client.get(f"/policies/{pid}")
    assert r2.status_code == 200
    assert r2.get_json()["coverage"] == 100000


def test_duplicate_policy(client):
    payload = {"customerId": 99, "coverage": 100000, "annualPremium": 300.0}
    r1 = client.post("/policies", json=payload)
    assert r1.status_code == 201

    r2 = client.post("/policies", json=payload)
    assert r2.status_code == 409
    assert "already has a policy" in r2.get_json()["detail"]