from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os, sys

### trying to use Alembic with Flask-SQLAlchemy 

# make importable
sys.path.append(os.path.abspath(os.getcwd()))
from app import create_app
from models import db, Policy               # import your models

config = context.config
fileConfig(config.config_file_name)

# point Alembic at the metadata
target_metadata = db.metadata

def get_url():
    return "postgresql://policy:pass@db_policy/policy_db"

def run_migrations_offline():
    context.configure(url=get_url(), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        {"sqlalchemy.url": get_url()},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()