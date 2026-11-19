"""
Blueprint for Driver Safety Profile routes.

Routes:
  POST   /driver/<id>  - Create Driver Safety Profile
  GET    /driver/<id>  - Retrieve Driver Safety Profile
  PUT    /driver/<id>  - Update Driver Safety Profile
  DELETE /driver/<id>  - Delete Driver Safety Profile
"""

from flask import Blueprint, request, jsonify

from app.auth import require_auth
from app import store

driver_bp = Blueprint("driver", __name__)


@driver_bp.route("/driver/<int:id>", methods=["POST"])
@require_auth
def create_driver_profile(id):
    if id in store.driver_profiles:
        return (
            jsonify(
                {
                    "error": {
                        "code": "PROFILE_ALREADY_EXISTS",
                        "message": f"A driver safety profile for driver {id} already exists.",
                        "details": {"driverId": id},
                    }
                }
            ),
            409,
        )

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

    profile = {
        "profileId": str(id),
        "driver": body.get(
            "driver",
            {
                "firstName": "",
                "lastName": "",
                "license": {
                    "issueDate": "",
                    "expiry": "",
                    "issuingState": "",
                    "restrictions": [],
                },
                "email": "",
            },
        ),
        "safetyScore": body.get("safetyScore", 100),
        "hardStops": body.get("hardStops", 0),
        "speeding": body.get("speeding", 0),
        "nightDrives": body.get("nightDrives", 0),
        "weather": body.get("weather", 0),
        "ignoredWarnings": body.get("ignoredWarnings", 0),
    }

    store.driver_profiles[id] = profile
    return jsonify(profile), 201


@driver_bp.route("/driver/<int:id>", methods=["GET"])
@require_auth
def get_driver_profile(id):
    profile = store.driver_profiles.get(id)
    if profile is None:
        return (
            jsonify(
                {
                    "error": {
                        "code": "PROFILE_NOT_FOUND",
                        "message": f"Driver safety profile for driver {id} was not found.",
                        "details": {"driverId": id},
                    }
                }
            ),
            404,
        )
    return jsonify(profile), 200


@driver_bp.route("/driver/<int:id>", methods=["PUT"])
@require_auth
def update_driver_profile(id):
    profile = store.driver_profiles.get(id)
    if profile is None:
        return (
            jsonify(
                {
                    "error": {
                        "code": "PROFILE_NOT_FOUND",
                        "message": f"Driver safety profile for driver {id} was not found.",
                        "details": {"driverId": id},
                    }
                }
            ),
            404,
        )

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

    # Full replacement of mutable fields
    for field in ("driver", "safetyScore", "hardStops", "speeding", "nightDrives", "weather", "ignoredWarnings"):
        if field in body:
            profile[field] = body[field]

    store.driver_profiles[id] = profile
    return jsonify(profile), 200


@driver_bp.route("/driver/<int:id>", methods=["DELETE"])
@require_auth
def delete_driver_profile(id):
    if id not in store.driver_profiles:
        return (
            jsonify(
                {
                    "error": {
                        "code": "PROFILE_NOT_FOUND",
                        "message": f"Driver safety profile for driver {id} was not found.",
                        "details": {"driverId": id},
                    }
                }
            ),
            404,
        )

    del store.driver_profiles[id]
    return "", 204
