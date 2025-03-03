# app/database/migrations/env.py
from multiprocessing import pool
from sqlalchemy import engine_from_config
from app import Config

def run_migrations_online():
    connectable = engine_from_config(
        {'sqlalchemy.url': Config.SQLALCHEMY_DATABASE_URI},
        prefix='sqlalchemy.',
        poolclass=pool.NullPool)