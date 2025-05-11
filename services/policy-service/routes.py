from flask import Blueprint, request, jsonify, abort
from models import db, Policy, PolicyType, Beneficiary
from schemas import PolicyCreate, PolicyOut, BeneficiaryIn
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
               annual_premium=data.annualPremium,
               policy_type=data.policyType)
    db.session.add(p)

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        # same pgcode for ALL dup-key errors
        if getattr(e.orig, "pgcode", None) == "23505":
            # check which unique constraint was hit
            if getattr(e.orig.diag, "constraint_name") == "ix_unique_active_type":
                return jsonify({"decision": "DECLINED",
                                "reason":   "policy_exists"}), 409
        # other DB errors
        return jsonify({"detail": "DB error"}), 500 


    #return (PolicyOut.model_validate(p).model_dump(by_alias=True, mode="json"), 201, )
    return _policy_to_json(p), 201


# get all policy numbers
@bp.get("/policies")
def search_policies():
    q = Policy.query
    cid = request.args.get("customerId", type=int)
    ptype = request.args.get("policyType")
    status = request.args.get("status")
    if cid:     q = q.filter_by(customer_id=cid)
    if ptype:   q = q.filter_by(policy_type=PolicyType(ptype))
    if status:  q = q.filter_by(status=status)
    return jsonify([p.id for p in q.all()]), 200


# get all policies for a customer
@bp.get("/customers/<int:cid>/policies")
def list_policies_for_customer(cid: int):
    status      = request.args.get("status")        # optional
    policy_type = request.args.get("policy_type")   # optional

    q = Policy.query.filter_by(customer_id=cid)
    if status:
        q = q.filter_by(status=status.upper())
    if policy_type:
        q = q.filter_by(policy_type=PolicyType(policy_type.upper()))

    # Return full JSON objects
    # payload = [
    #     PolicyOut.model_validate(p).model_dump(by_alias=True, mode="json")
    #     for p in q.order_by(Policy.policy_type, Policy.id)
    # ]
    # return jsonify(payload), 200

    payload = [_policy_to_json(p) for p in q.order_by(Policy.policy_type, Policy.id)]
    return jsonify(payload), 200





# read for specific policy
@bp.get("/policies/<int:pid>")
def get_policy(pid: int):
    p = Policy.query.get_or_404(pid)
    #return (PolicyOut.model_validate(p).model_dump(by_alias=True, mode="json"), 200, )
    return _policy_to_json(p), 200


# update coverage / status
@bp.patch("/policies/<int:pid>")
def patch_policy(pid):
    p = Policy.query.get_or_404(pid)
    data = request.json or {}
    if "coverage" in data:
        p.coverage = data["coverage"]
    if "status" in data:
        p.status = data["status"]
    db.session.commit()
    
    #return PolicyOut.model_validate(p).model_dump(by_alias=True, mode="json"), 200
    return _policy_to_json(p), 200


# soft delete (lapse)
@bp.delete("/policies/<int:pid>")
def lapse_policy(pid):
    p = Policy.query.get_or_404(pid)
    p.status = "LAPSED"
    db.session.commit()
    return "", 204

# add beneficiaries
@bp.post("/policies/<int:pid>/beneficiaries")
def set_beneficiaries(pid):
    p = Policy.query.get_or_404(pid)
    benes = [BeneficiaryIn.model_validate(b) for b in request.json]
    if round(sum(b.pctShare for b in benes), 2) != 100:
        return jsonify(detail="pctShare must total 100%"), 400

    # replace existing
    Beneficiary.query.filter_by(policy_id=pid).delete()
    db.session.flush()
    for b in benes:
        db.session.add(Beneficiary(policy_id=pid,
                                   name=b.name,
                                   pct_share=b.pctShare))
    db.session.commit()
    return {"policyId": pid, "beneficiaries": [b.model_dump() for b in benes]}, 200



# helper functions
def _policy_to_json(p: Policy) -> dict:
    data = PolicyOut.model_validate(p).model_dump(by_alias=True, mode="json")
    data["beneficiaries"] = [
        {"name": b.name, "pctShare": float(b.pct_share)}
        for b in p.beneficiaries
    ]
    return data