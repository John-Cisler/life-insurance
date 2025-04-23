from flask import Flask, request, jsonify
from models import db, Customer

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://cust:pass@db_customer/customer_db"
db.init_app(app)

@app.post("/customers")
def create_customer():
    data = request.json
    c = Customer(**data)
    db.session.add(c); db.session.commit()
    return jsonify({"customerId": c.id}), 201

@app.get("/customers/<int:cid>")
def fetch_customer(cid):
    c = Customer.query.get_or_404(cid)
    return jsonify({"id": c.id,
                    "firstName": c.first_name,
                    "smoker": c.smoker})

