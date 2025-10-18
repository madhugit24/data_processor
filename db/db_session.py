import os
from flask import g
from flask_sqlalchemy import SQLAlchemy


def configure_db_session(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI", "")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = os.getenv(
        "SQLALCHEMY_TRACK_MODIFICATIONS", ""
    )
    app.config["SQLALCHEMY_POOL_SIZE"] = os.getenv("SQLALCHEMY_POOL_SIZE", "")
    app.config["SQLALCHEMY_MAX_OVERFLOW"] = os.getenv("SQLALCHEMY_MAX_OVERFLOW", "")
    app.config["SQLALCHEMY_POOL_TIMEOUT"] = os.getenv("SQLALCHEMY_POOL_TIMEOUT", "")
    app.config["SQLALCHEMY_POOL_RECYCLE"] = os.getenv("SQLALCHEMY_POOL_RECYCLE", "")

    db = SQLAlchemy(
        app,
        session_options={
            "autocommit": False,
            "autoflush": False,
            "expire_on_commit": False,
        },
    )

    @app.teardown_appcontext
    def close_session(exception=None):
        db.session.remove()

    @app.before_request
    def attach_session():
        g.session = db.session