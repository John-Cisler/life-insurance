from flask import Flask, jsonify
from models import db
from routes import bp

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "postgresql://policy:pass@db_policy/policy"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    app.register_blueprint(bp)
    return app

app = create_app()

@app.errorhandler(404)
def not_found(e): return jsonify(detail=str(e)), 404