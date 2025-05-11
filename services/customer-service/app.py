from flask import Flask, request, jsonify
from models import db, Customer
from datetime import datetime
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://cust:pass@db_customer/cust"
db.init_app(app)

with app.app_context():
    db.create_all()

# error handler
@app.errorhandler(404)
def not_found(e):
    return jsonify(detail=str(e)), 404

# helpers
def customer_to_dict(c: Customer):
    return {
        "id": c.id,
        "firstName": c.first_name,
        "lastName":  c.last_name,
        "dob":       c.dob.isoformat(),
        "smoker":    c.smoker,
        "isActive":  c.is_active,
        "createdAt": c.created_at.isoformat()
    }

# create
@app.post("/customers")
def create_customer():
    data = request.get_json(force=True)
    try:
        c = Customer(
            first_name=data["first_name"],
            last_name=data["last_name"],
            dob=datetime.fromisoformat(data["dob"]).date(),
            smoker=data.get("smoker", False)
        )
        db.session.add(c)
        db.session.commit()
    except (KeyError, ValueError) as exc:
        return jsonify(detail=f"Invalid payload: {exc}"), 400
    return jsonify({"customerId": c.id}), 201

# reinstate
@app.post("/customers/<int:cid>/reinstate")
def reinstate_customer(cid):
    """
    Reactivate a previously soft-deleted customer.
    """
    c = Customer.query.filter_by(id=cid, is_active=False).first()
    if not c:
        return jsonify(detail=f"Customer {cid} not found or already active"), 404

    c.is_active = True
    db.session.commit()
    return jsonify({"customerId": c.id, "status": "reactivated"}), 200

# read
@app.get("/customers/<int:cid>")
def fetch_customer(cid):
    c = Customer.query.filter_by(id=cid, is_active=True).first_or_404()
    return jsonify(customer_to_dict(c)), 200

# full update
@app.put("/customers/<int:cid>")
def replace_customer(cid):
    c = Customer.query.filter_by(id=cid, is_active=True).first_or_404()
    data = request.get_json(force=True)
    try:
        c.first_name = data["first_name"]
        c.last_name  = data["last_name"]
        c.dob        = datetime.fromisoformat(data["dob"]).date()
        c.smoker     = data.get("smoker", c.smoker)
        db.session.commit()
    except (KeyError, ValueError) as exc:
        return jsonify(detail=f"Invalid payload: {exc}"), 400
    return jsonify(customer_to_dict(c)), 200

# partial update
@app.patch("/customers/<int:cid>")
def patch_customer(cid):
    c = Customer.query.filter_by(id=cid, is_active=True).first_or_404()
    data = request.get_json(force=True)
    try:
        if "first_name" in data: c.first_name = data["first_name"]
        if "last_name"  in data: c.last_name  = data["last_name"]
        if "dob"        in data: c.dob = datetime.fromisoformat(data["dob"]).date()
        if "smoker"     in data: c.smoker = bool(data["smoker"])
        db.session.commit()
    except ValueError as exc:
        return jsonify(detail=f"Invalid payload: {exc}"), 400
    return jsonify(customer_to_dict(c)), 200

# delete / deactivate
@app.delete("/customers/<int:cid>")
def delete_customer(cid):
    c = Customer.query.filter_by(id=cid, is_active=True).first_or_404()
    c.is_active = False                 # soft delete
    db.session.commit()
    return "", 204