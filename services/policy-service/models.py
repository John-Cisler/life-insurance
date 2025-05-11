from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import datetime
import enum

db = SQLAlchemy()

class PolicyType(enum.Enum):
    TERM  = "TERM"
    WHOLE = "WHOLE"

class Policy(db.Model):
    __tablename__ = "policies"
    id            = db.Column(db.Integer, primary_key=True)
    customer_id   = db.Column(db.Integer, nullable=False)
    coverage      = db.Column(db.Integer, nullable=False)
    annual_premium= db.Column(db.Numeric(10,2), nullable=False)
    policy_type   = db.Column(db.Enum(PolicyType), nullable=False, default=PolicyType.TERM)
    status        = db.Column(db.String(20), default="ACTIVE")   # ACTIVE|LAPSED|CANCELLED
    issued_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    beneficiaries = db.relationship(
        "Beneficiary",
        backref="policy",                     # Beneficiary.policy points back
        cascade="all, delete-orphan",
        lazy="selectin"                    # fetch all beneficiaries in one go    
    )

    

class Beneficiary(db.Model):
    __tablename__ = "beneficiaries"
    id          = db.Column(db.Integer, primary_key=True)
    policy_id   = db.Column(db.Integer, db.ForeignKey('policies.id', ondelete="CASCADE"))
    name        = db.Column(db.String(80), nullable=False)
    pct_share   = db.Column(db.Numeric(5,2), nullable=False)