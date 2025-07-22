# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()
cors = CORS()

def init_app(app):
    db.init_app(app)
    with app.app_context():
        # This makes db.engine available at import time
        db.engine.url