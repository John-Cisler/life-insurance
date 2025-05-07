from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import datetime

db = SQLAlchemy()

class Policy(db.Model):
    __tablename__ = "policies"
    id            = db.Column(db.Integer, primary_key=True)
    customer_id   = db.Column(db.Integer, nullable=False)
    coverage      = db.Column(db.Integer, nullable=False)
    annual_premium= db.Column(db.Numeric(10, 2), nullable=False)
    status        = db.Column(db.String(20), default="ACTIVE")
    issued_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    __table_args__ = (
        db.UniqueConstraint("customer_id", name="uq_policy_customer"),  # restrict people to one policy for now -- maybe we only allow for one type of insurance
    )