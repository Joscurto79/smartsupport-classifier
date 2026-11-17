from datetime import datetime, timezone
from flask import Blueprint, jsonify, request
from app.classifier import analyze_ticket

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")


@api_bp.route("/classify", methods=["POST"])
def classify_ticket():
    payload = request.get_json(silent=True)

    # Pillar 1: Input Validation Guardrail (HTTP 400)
    if not payload or not isinstance(payload, dict):
        return jsonify({
            "error": "VALIDATION_ERROR",
            "message": "Request body must be valid JSON",
        }), 400

    ticket_id = payload.get("ticket_id")
    text = payload.get("text")

    if (
        not ticket_id
        or not isinstance(ticket_id, str)
        or not text
        or not isinstance(text, str)
        or len(text.strip()) < 5
    ):
        return jsonify({
            "error": "VALIDATION_ERROR",
            "message": "Valid 'ticket_id' and 'text' (min 5 chars) are required",
        }), 400

    # Pillar 2: Delegate NLP Inference
    analysis = analyze_ticket(text.strip())
    urgency = analysis["urgency_score"]

    # Pillar 3: 3-Tier Operational Routing Thresholds
    if urgency >= 0.80:
        routing_queue = "Critical_Escalations"
        requires_manual_triage = False
    elif urgency >= 0.60:
        routing_queue = "Triage_Queue"
        requires_manual_triage = True
    else:
        routing_queue = "Standard_Support"
        requires_manual_triage = False

    # Pillar 4: Auditable API Response Contract (HTTP 200)
    response_body = {
        "ticket_id": ticket_id.strip(),
        "category": analysis["category"],
        "urgency_score": urgency,
        "sentiment": analysis["sentiment"],
        "routing_queue": routing_queue,
        "requires_manual_triage": requires_manual_triage,
        "model_version": analysis["model_version"],
        "processed_at": datetime.now(timezone.utc).isoformat(),
    }

    return jsonify(response_body), 200