from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Customer(db.Model):
    __tablename__ = "customers"
    id           = db.Column(db.Integer, primary_key=True)
    first_name   = db.Column(db.String(30))
    last_name    = db.Column(db.String(30))
    dob          = db.Column(db.Date)
    smoker       = db.Column(db.Boolean)
    created_at   = db.Column(db.DateTime, server_default=db.func.now())
    is_active   = db.Column(db.Boolean, default=True)