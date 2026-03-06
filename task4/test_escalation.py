import pytest
from escalation import should_escalate
from models import CustomerContext


def mock_context(vip=False, overdue=False, tickets=None, complete=True):

    return CustomerContext(
        phone="123",
        crm_data={"vip": vip},
        billing_data={"status": "overdue" if overdue else "paid"},
        ticket_data={"recent_tickets": tickets or []},
        data_complete=complete,
        fetch_time_ms=200
    )


def test_low_confidence():
    """Escalate when AI confidence is below threshold to avoid incorrect responses."""
    ctx = mock_context()
    assert should_escalate(ctx, 0.5, 0.1, "network_issue")[0]


def test_angry_customer():
    """Escalate when sentiment is very negative because angry users require human support."""
    ctx = mock_context()
    assert should_escalate(ctx, 0.9, -0.7, "billing")[0]


def test_repeat_complaint():
    """Escalate when the same complaint appears multiple times indicating unresolved issue."""
    ctx = mock_context(tickets=["network", "network", "network"])
    assert should_escalate(ctx, 0.9, 0.1, "network")[0]


def test_service_cancellation():
    """Cancellation requests always require human confirmation."""
    ctx = mock_context()
    assert should_escalate(ctx, 0.9, 0.1, "service_cancellation")[0]


def test_vip_billing_issue():
    """VIP customers with overdue billing should receive priority human support."""
    ctx = mock_context(vip=True, overdue=True)
    assert should_escalate(ctx, 0.9, 0.1, "billing")[0]


def test_incomplete_data():
    """Escalate when system lacks enough data and confidence is low."""
    ctx = mock_context(complete=False)
    assert should_escalate(ctx, 0.7, 0.1, "network")[0]


def test_ai_can_handle():
    """Normal scenario where AI has high confidence and no escalation rule applies."""
    ctx = mock_context()
    result = should_escalate(ctx, 0.9, 0.1, "network")
    assert result == (False, "ai_can_handle")


def test_edge_boundary_confidence():
    """Edge case: confidence exactly at threshold should NOT trigger escalation."""
    ctx = mock_context()
    result = should_escalate(ctx, 0.65, 0.1, "network")
    assert result[0] is False