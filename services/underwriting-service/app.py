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
    try:
        data = UWRequest.model_validate(request.json)
    except ValidationError as e:
        return jsonify(e.errors()), 400
    cust = fetch_customer(data.customerId)
    premium, decision = calculate_premium(cust, data.coverage)
    return jsonify({"customerId": data.customerId,
                    "decision": decision,
                    "annualPremium": premium})