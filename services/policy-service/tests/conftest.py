# services/policy-service/tests/conftest.py
import os
import tempfile
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import create_app
from models import db as _db, Policy


# 1. Flask application fixture
@pytest.fixture(scope="session")
def app():
    """
    Returns a Flask app object configured for tests.
    Creates a temporary SQLite file so every test run starts clean.
    """
    # Use a temp file-based SQLite DB so metadata.create_all() works
    db_fd, db_path = tempfile.mkstemp()
    test_db_uri = f"sqlite:///{db_path}"

    app = create_app()
    app.config.update(
        SQLALCHEMY_DATABASE_URI=test_db_uri,
        TESTING=True,
        WTF_CSRF_ENABLED=False,
    )

    with app.app_context():
        _db.create_all()  # create tables

    yield app

    # Teardown
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(scope="function")
def db_session(app):
    """
    Provide a SQLAlchemy session that rolls back after each test.
    """
    connection = _db.engine.connect()
    transaction = connection.begin()
    options = dict(bind=connection, binds={})
    session = _db.create_scoped_session(options=options)

    # Overwrite the global session to this function-level session
    _db.session = session

    yield session    # here your test runs

    transaction.rollback()
    connection.close()
    session.remove()


# Flask test client fixture
@pytest.fixture(scope="function")
def client(app, db_session):
    """
    Flask test client that uses the db_session fixture.
    """
    return app.test_client()