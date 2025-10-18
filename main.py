from flask import Flask

from db.db_session import configure_db_session
from utils.routes import register_routes
from utils.logger import configure_logging, configure_request_handler
from logging.config import dictConfig


def create_app():
    dictConfig(configure_logging())
    app = Flask(__name__)
    configure_db_session(app)
    configure_request_handler(app)
    register_routes(app)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)