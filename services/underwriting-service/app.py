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


@app.post("/quote")
def quote_only():
    try:
        data = UWRequest.model_validate(request.json)
    except ValidationError as e:
        return jsonify(e.errors()), 400

    cust = fetch_customer(data.customerId)
    premium, decision = calculate_premium(cust, data.coverage)

    return jsonify({
        "customerId":   data.customerId,
        "decision":     decision,
        "annualPremium": premium
    }), 200



@app.post("/underwrite")
def underwrite():
    try:
        data = UWRequest.model_validate(request.json)
    except ValidationError as e:
        return jsonify(e.errors()), 400

    policy_type = request.args.get("policy_type", "TERM").upper()

    cust = fetch_customer(data.customerId)
    premium, decision = calculate_premium(cust, data.coverage)

    # duplicate policy guard
    if decision == "APPROVED":
        chk_url = (
            "http://policy-service:8083/policies"
            f"?customerId={data.customerId}&policyType={policy_type}&status=ACTIVE"
        )
        dup_resp = requests.get(chk_url, timeout=5)
        dup_resp.raise_for_status()
        if dup_resp.json():          # non-empty list
            return jsonify({
                "decision": "DECLINED",
                "reason":   "policy_exists"
            }), 409

    # strict-consistency policy creation 
    policy_data = None
    status_code = 200
    if decision == "APPROVED":
        policy_resp = requests.post(
            "http://policy-service:8083/policies",
            json={
                "customerId":   data.customerId,
                "coverage":     data.coverage,
                "annualPremium": premium,
                "policyType":   policy_type
            },
            timeout=5
        )

        if policy_resp.status_code != 201:
            return jsonify({"detail": "Policy creation failed"}), 500

        policy_data = policy_resp.json()
        status_code = 201

    # build response
    body = {
        "customerId":   data.customerId,
        "decision":     decision,
        "annualPremium": premium,
        "policyType":   policy_type
    }
    if policy_data:
        body.update({
            "policyId": policy_data["id"],
            "policyLink": f"/policies/{policy_data['id']}"
        })
    return jsonify(body), status_code