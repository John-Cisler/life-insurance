from flask import Blueprint, request, jsonify, abort
from models import db, Policy
from schemas import PolicyCreate, PolicyOut
from sqlalchemy.exc import IntegrityError

bp = Blueprint("policy", __name__)

@bp.post("/policies")
def create_policy():
    try:
        data = PolicyCreate.model_validate(request.json, from_attributes=True)
    except ValueError as e:
        return jsonify({"detail": str(e)}), 400

    p = Policy(customer_id=data.customerId,
               coverage=data.coverage,
               annual_premium=data.annualPremium)
    db.session.add(p)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        # detect UNIQUE constraint breach
        if getattr(e.orig, 'pgcode', None) == '23505':          # Postgres adapter error
            return jsonify({
                "detail": f"Customer {data.customerId} already has a policy"
            }), 409
        # other DB errors
        return jsonify({"detail": "DB error"}), 500 


    return (PolicyOut.model_validate(p).model_dump(by_alias=True, mode="json"), 201, )


@bp.get("/policies/<int:pid>")
def get_policy(pid: int):
    p = Policy.query.get_or_404(pid)
    return (PolicyOut.model_validate(p).model_dump(by_alias=True, mode="json"), 200, )