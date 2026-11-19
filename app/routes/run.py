"""
Blueprint for Safety Scan Run routes.

Routes:
  POST   /run          - Start a safety scan run
  GET    /run/<id>     - Get run status
  DELETE /run/<id>     - Cancel a run
"""

from flask import Blueprint, request, jsonify

from app.auth import require_auth
from app import store

run_bp = Blueprint("run", __name__)


@run_bp.route("/run", methods=["POST"])
@require_auth
def start_run():
    body = request.get_json(silent=True)
    if not body:
        return (
            jsonify(
                {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Request body is required.",
                        "details": {"fields": ["body"]},
                    }
                }
            ),
            400,
        )

    vehicle_id = body.get("vehicle")
    driver_id = body.get("driver")

    if not vehicle_id or not driver_id:
        return (
            jsonify(
                {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Both 'vehicle' and 'driver' fields are required.",
                        "details": {"fields": ["vehicle", "driver"]},
                    }
                }
            ),
            400,
        )

    run_id = store.next_run_id()
    run = {
        "run": str(run_id),
        "status": "QUEUED",
        "vehicle": vehicle_id,
        "driver": driver_id,
    }
    store.runs[run_id] = run
    return jsonify({"run": str(run_id), "status": "QUEUED"}), 201


@run_bp.route("/run/<int:id>", methods=["GET"])
@require_auth
def get_run(id):
    run = store.runs.get(id)
    if run is None:
        return (
            jsonify(
                {
                    "error": {
                        "code": "PROFILE_NOT_FOUND",
                        "message": f"Run {id} was not found.",
                        "details": {"runId": id},
                    }
                }
            ),
            404,
        )

    # Simulate progression: once retrieved, mark as COMPLETE
    run["status"] = "COMPLETE"
    store.runs[id] = run
    return jsonify({"run": str(id), "status": run["status"]}), 200


@run_bp.route("/run/<int:id>", methods=["DELETE"])
@require_auth
def cancel_run(id):
    run = store.runs.get(id)
    if run is None:
        return (
            jsonify(
                {
                    "error": {
                        "code": "PROFILE_NOT_FOUND",
                        "message": f"Run {id} was not found.",
                        "details": {"runId": id},
                    }
                }
            ),
            404,
        )

    run["status"] = "CANCELLED"
    store.runs[id] = run
    return "", 204
