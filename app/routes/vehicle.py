"""
Blueprint for Vehicle Safety Profile routes.

Routes:
  POST   /vehicle/<id>  - Create Vehicle Safety Profile
  GET    /vehicle/<id>  - Retrieve Vehicle Safety Profile
  PATCH  /vehicle/<id>  - Update Vehicle Safety Profile
  DELETE /vehicle/<id>  - Delete Vehicle Safety Profile
"""

import uuid
from datetime import datetime, timezone

from flask import Blueprint, request, jsonify

from app.auth import require_auth
from app import store

vehicle_bp = Blueprint("vehicle", __name__)

_VEHICLE_LOOKUP = {
    # Simple VIN-prefix → make/model/year mapping for demo realism
    "1HG": ("Honda", "Civic", 2022),
    "1HGC": ("Honda", "Accord", 2021),
    "1G1": ("Chevrolet", "Malibu", 2020),
    "JTD": ("Toyota", "Corolla", 2023),
    "WBA": ("BMW", "3 Series", 2022),
}


def _infer_vehicle_info(vin: str):
    for prefix, info in _VEHICLE_LOOKUP.items():
        if vin.upper().startswith(prefix):
            return info
    return ("Toyota", "Camry", 2021)


def _calculate_risk_score(body: dict) -> int:
    """Simple heuristic: each non-OK component adds points; each active code adds points."""
    score = 0
    components = ["tpms", "tailLights", "oilPressure", "sensors", "defrost", "airbags", "battery"]
    for comp in components:
        if body.get(comp, "OK") != "OK":
            score += 10
    active_codes = body.get("activeCodes", [])
    score += len(active_codes) * 6
    if body.get("newCode"):
        score += 5
    return min(score, 100)


@vehicle_bp.route("/vehicle/<int:id>", methods=["POST"])
@require_auth
def create_vehicle_profile(id):
    if id in store.vehicle_profiles:
        return (
            jsonify(
                {
                    "error": {
                        "code": "PROFILE_ALREADY_EXISTS",
                        "message": f"A vehicle safety profile for vehicle {id} already exists.",
                        "details": {"vehicleId": id},
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

    vin = body.get("vin", "UNKNOWN")
    make, model, year = _infer_vehicle_info(vin)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

    profile = {
        "vehicleId": str(uuid.uuid4()),
        "profileId": str(uuid.uuid4()),
        "createdAt": now,
        "updatedAt": now,
        "status": "ACTIVE",
        "riskScore": _calculate_risk_score(body),
        "vin": vin,
        "make": make,
        "model": model,
        "year": year,
        "tpms": body.get("tpms", "OK"),
        "tailLights": body.get("tailLights", "OK"),
        "oilPressure": body.get("oilPressure", "OK"),
        "sensors": body.get("sensors", "OK"),
        "defrost": body.get("defrost", "OK"),
        "airbags": body.get("airbags", "OK"),
        "battery": body.get("battery", "OK"),
        "newCode": body.get("newCode", False),
        "activeCodes": body.get("activeCodes", []),
        "metrics": {
            "hardCorneringEvents": 0,
            "hardBrakingEvents": 0,
            "speedingEvents": 0,
        },
    }

    store.vehicle_profiles[id] = profile
    return jsonify(profile), 201


@vehicle_bp.route("/vehicle/<int:id>", methods=["GET"])
@require_auth
def get_vehicle_profile(id):
    profile = store.vehicle_profiles.get(id)
    if profile is None:
        return (
            jsonify(
                {
                    "error": {
                        "code": "PROFILE_NOT_FOUND",
                        "message": f"Vehicle safety profile for vehicle {id} was not found.",
                        "details": {"vehicleId": id},
                    }
                }
            ),
            404,
        )
    return jsonify(profile), 200


@vehicle_bp.route("/vehicle/<int:id>", methods=["PATCH"])
@require_auth
def update_vehicle_profile(id):
    profile = store.vehicle_profiles.get(id)
    if profile is None:
        return (
            jsonify(
                {
                    "error": {
                        "code": "PROFILE_NOT_FOUND",
                        "message": f"Vehicle safety profile for vehicle {id} was not found.",
                        "details": {"vehicleId": id},
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

    patchable = [
        "tpms", "tailLights", "oilPressure", "sensors", "defrost",
        "airbags", "battery", "newCode", "activeCodes", "status", "metrics",
    ]
    for field in patchable:
        if field in body:
            profile[field] = body[field]

    profile["riskScore"] = _calculate_risk_score(profile)
    profile["updatedAt"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    store.vehicle_profiles[id] = profile
    return jsonify(profile), 200


@vehicle_bp.route("/vehicle/<int:id>", methods=["DELETE"])
@require_auth
def delete_vehicle_profile(id):
    if id not in store.vehicle_profiles:
        return (
            jsonify(
                {
                    "error": {
                        "code": "PROFILE_NOT_FOUND",
                        "message": f"Vehicle safety profile for vehicle {id} was not found.",
                        "details": {"vehicleId": id},
                    }
                }
            ),
            404,
        )

    del store.vehicle_profiles[id]
    return "", 204
