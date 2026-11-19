"""
SafeStar Service API — Flask application entry point.

Registers all route blueprints and configures the app.
"""

from flask import Flask, jsonify

from app.routes.driver import driver_bp
from app.routes.vehicle import vehicle_bp
from app.routes.run import run_bp
from app.routes.display import display_bp
from app.routes.diagnostics import diagnostics_bp


def create_app() -> Flask:
    app = Flask(__name__)

    # ── Register blueprints ──────────────────────────────────────────────────
    app.register_blueprint(driver_bp)
    app.register_blueprint(vehicle_bp)
    app.register_blueprint(run_bp)
    app.register_blueprint(display_bp)
    app.register_blueprint(diagnostics_bp)

    # ── Global error handlers ────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return (
            jsonify(
                {
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "The requested resource was not found.",
                        "details": {},
                    }
                }
            ),
            404,
        )

    @app.errorhandler(405)
    def method_not_allowed(e):
        return (
            jsonify(
                {
                    "error": {
                        "code": "METHOD_NOT_ALLOWED",
                        "message": "The HTTP method is not allowed for this endpoint.",
                        "details": {},
                    }
                }
            ),
            405,
        )

    @app.errorhandler(500)
    def internal_error(e):
        return (
            jsonify(
                {
                    "error": {
                        "code": "UNEXPECTED_ERROR",
                        "message": "An unexpected error occurred.",
                        "details": {},
                    }
                }
            ),
            500,
        )

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=5000, debug=True)
