from models import CustomerContext


def should_escalate(context: CustomerContext,
                    confidence_score: float,
                    sentiment_score: float,
                    intent: str) -> tuple[bool, str]:

    # Rule 1
    if confidence_score < 0.65:
        return True, "low_confidence"

    # Rule 2
    if sentiment_score < -0.6:
        return True, "angry_customer"

    # Rule 3
    if context.ticket_data:
        tickets = context.ticket_data.get("recent_tickets", [])
        if tickets.count(intent) >= 3:
            return True, "repeat_complaint"

    # Rule 4
    if intent == "service_cancellation":
        return True, "service_cancellation"

    # Rule 5
    if context.crm_data and context.billing_data:
        if context.crm_data.get("vip") and context.billing_data.get("status") == "overdue":
            return True, "vip_billing_issue"

    # Rule 6
    if not context.data_complete and confidence_score < 0.80:
        return True, "incomplete_data"

    return False, "ai_can_handle"