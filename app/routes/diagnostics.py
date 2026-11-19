"""
Blueprint for Diagnostics / Reporting routes.

Routes:
  POST /diagnostics/generate/<vehicle_id>  - Run diagnostic and generate report
  GET  /diagnostics/<id>                   - Retrieve diagnostic report
  POST /diagnostics/send/<id>              - Send diagnostic report
"""

from datetime import datetime, timezone

from flask import Blueprint, request, jsonify

from app.auth import require_auth
from app import store

diagnostics_bp = Blueprint("diagnostics", __name__)


def _build_report(vehicle_id: int, vehicle_profile: dict) -> dict:
    """Construct a full diagnostic report from a vehicle profile."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    active_codes = vehicle_profile.get("activeCodes", [])
    risk_score = vehicle_profile.get("riskScore", 0)

    components = {
        "tpms": vehicle_profile.get("tpms", "OK"),
        "tailLights": vehicle_profile.get("tailLights", "OK"),
        "oilPressure": vehicle_profile.get("oilPressure", "OK"),
        "sensors": vehicle_profile.get("sensors", "OK"),
        "defrost": vehicle_profile.get("defrost", "OK"),
        "airbags": vehicle_profile.get("airbags", "OK"),
        "battery": vehicle_profile.get("battery", "OK"),
    }

    failed = [k for k, v in components.items() if v != "OK"]
    overall_status = "PASS" if not failed and not active_codes else "FAIL"

    findings = []
    for code in active_codes:
        findings.append(
            {
                "code": code,
                "severity": "HIGH" if code.startswith("P0") else "MEDIUM",
                "description": f"OBD-II fault code {code} detected. Immediate inspection recommended.",
                "recommendation": "Schedule a service appointment.",
            }
        )
    for comp in failed:
        findings.append(
            {
                "code": f"COMP_{comp.upper()}_FAIL",
                "severity": "MEDIUM",
                "description": f"Component '{comp}' reported a non-OK status: {components[comp]}.",
                "recommendation": f"Inspect and repair the {comp} system.",
            }
        )

    return {
        "vehicleId": vehicle_id,
        "vin": vehicle_profile.get("vin", "UNKNOWN"),
        "make": vehicle_profile.get("make", ""),
        "model": vehicle_profile.get("model", ""),
        "year": vehicle_profile.get("year", 0),
        "generatedAt": now,
        "overallStatus": overall_status,
        "riskScore": risk_score,
        "components": components,
        "activeCodes": active_codes,
        "findings": findings,
        "metrics": vehicle_profile.get(
            "metrics",
            {"hardCorneringEvents": 0, "hardBrakingEvents": 0, "speedingEvents": 0},
        ),
        "sentAt": None,
        "sentTo": None,
    }


@diagnostics_bp.route("/diagnostics/generate/<int:vehicle_id>", methods=["POST"])
@require_auth
def generate_diagnostic(vehicle_id):
    vehicle_profile = store.vehicle_profiles.get(vehicle_id)
    if vehicle_profile is None:
        return (
            jsonify(
                {
                    "error": {
                        "code": "PROFILE_NOT_FOUND",
                        "message": f"Vehicle safety profile for vehicle {vehicle_id} was not found.",
                        "details": {"vehicleId": vehicle_id},
                    }
                }
            ),
            404,
        )

    diag_id = store.next_diagnostic_id()
    report = _build_report(vehicle_id, vehicle_profile)
    report["diagnosticId"] = str(diag_id)
    store.diagnostics[diag_id] = report

    return jsonify({"status": "queued", "id": str(diag_id)}), 201


@diagnostics_bp.route("/diagnostics/<int:id>", methods=["GET"])
@require_auth
def get_diagnostic(id):
    report = store.diagnostics.get(id)
    if report is None:
        return (
            jsonify(
                {
                    "error": {
                        "code": "PROFILE_NOT_FOUND",
                        "message": f"Diagnostic report {id} was not found.",
                        "details": {"diagnosticId": id},
                    }
                }
            ),
            404,
        )
    return jsonify(report), 200


@diagnostics_bp.route("/diagnostics/send/<int:id>", methods=["POST"])
@require_auth
def send_diagnostic(id):
    report = store.diagnostics.get(id)
    if report is None:
        return (
            jsonify(
                {
                    "error": {
                        "code": "PROFILE_NOT_FOUND",
                        "message": f"Diagnostic report {id} was not found.",
                        "details": {"diagnosticId": id},
                    }
                }
            ),
            404,
        )

    body = request.get_json(silent=True) or {}
    recipient = body.get("email") or body.get("recipient") or "on-file"

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    report["sentAt"] = now
    report["sentTo"] = recipient
    store.diagnostics[id] = report

    return (
        jsonify(
            {
                "diagnosticId": str(id),
                "status": "SENT",
                "sentAt": now,
                "sentTo": recipient,
            }
        ),
        200,
    )
