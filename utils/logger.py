from flask import g, jsonify, request
import os
import time
from datetime import datetime


def configure_logging():
    """Configure logging for the application."""
    # Create logs folder if not present
    if not os.path.exists("logs"):
        os.makedirs("logs")

    return {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] | [%(levelname)s] | [%(module)s] | [%(message)s]",
                "datefmt": "%B %d, %Y %H:%M:%S %Z",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
            "file": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "filename": "logs/app.log",
                "when": "midnight",
                "backupCount": 5,
                "formatter": "default",
            },
        },
        "root": {
            "level": f"{os.getenv('LOG_LEVEL', 'DEBUG')}",
            "handlers": ["console", "file"],
        },
    }


def configure_request_handler(app):
    """
    Configure request handler for the application.
    """

    @app.before_request
    def log_request_info():
        g.logger = app.logger
        request.start_time = time.time()
        app.logger.info("Headers: %s", request.headers)
        app.logger.info("Body: %s", request.get_data())

    @app.after_request
    def logAfterRequest(response):
        """Log the response."""
        app.logger.info(
            "path: %s | method: %s | status: %s | size: %s",
            request.path,
            request.method,
            response.status,
            response.content_length,
        )
        request.end_time = time.time()
        total_time = request.end_time - request.start_time
        app.logger.info(f"Total request time: {total_time:.2f} seconds")

        return response

    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f"Unhandled exception: {e}", exc_info=True)
        return jsonify({"error": "Internal Server Error"}), 500