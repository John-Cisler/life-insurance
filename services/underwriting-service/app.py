from flask import Flask, request, jsonify
from pydantic import BaseModel, ValidationError
import yaml, requests, datetime as dt

rules = yaml.safe_load(open("rules.yaml"))

class UWRequest(BaseModel):
    customerId: int
    coverage:   int  # e.g. $ amount

app = Flask(__name__)

def fetch_customer(cid):
    resp = requests.get(f"http://customer-service:8081/customers/{cid}")
    resp.raise_for_status()
    return resp.json()

def calculate_premium(cust, coverage):
    age = int((dt.date.today() - dt.date.fromisoformat(cust["dob"])).days / 365.25)
    if age < rules["min_age"] or age > rules["max_age"]:
        return None, "DECLINED"
    premium = rules["base_premium"] * (coverage / 100000)
    if cust["smoker"]:
        premium *= 1 + rules["smoker_surcharge_pct"]
    return round(premium, 2), "APPROVED"

@app.post("/underwrite")
def underwrite():
    # validate input 
    try:
        data = UWRequest.model_validate(request.json)
    except ValidationError as e:
        return jsonify(e.errors()), 400

    cust = fetch_customer(data.customerId)
    premium, decision = calculate_premium(cust, data.coverage)

    # prepare holder so it's in scope no matter what
    policy_data = None
    status_code  = 200          # default

    # Strict‑consistency branch
    if decision == "APPROVED":
        policy_resp = requests.post(
            "http://policy-service:8083/policies",
            json={
                "customerId": data.customerId,
                "coverage":   data.coverage,
                "annualPremium": premium
            },
            timeout=5
        )

        print("UW → Policy status=", policy_resp.status_code,
        "body=", policy_resp.text, flush=True)

        if policy_resp.status_code == 409:         # already has a policy
            return jsonify({
                "decision": "DECLINED",
                "reason":   "policy_exists"
            }), 409

        if policy_resp.status_code != 201:         # any other failure
            return jsonify({"detail": "Policy creation failed"}), 500

        # success -> grab JSON so caller can see it
        policy_data = policy_resp.json()
        status_code = 201                          # created

    # Build unified response 
    response_body = {
        "customerId":   data.customerId,
        "decision":     decision,
        "annualPremium": premium,
    }


    if policy_data:
        response_body.update({
            "policyId":   policy_data["id"],
            "policyLink": f"/policies/{policy_data['id']}"
        })

    return jsonify(response_body), status_code