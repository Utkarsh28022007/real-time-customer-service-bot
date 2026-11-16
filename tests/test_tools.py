import pytest
from backend.app.tools.registry import check_order_status, create_ticket, get_faq, normalize_order_id
from backend.app.db.database import init_db


def test_normalize_order_id():
    assert normalize_order_id("88421") == "ORD-88421"
    assert normalize_order_id("ord-88421") == "ORD-88421"
    assert normalize_order_id("ORD-88421") == "ORD-88421"


def test_check_order_status_found():
    result = check_order_status("ORD-88421")
    assert result["found"] is True
    assert result["status"] == "In Transit"
    assert result["carrier"] == "FedEx"
    assert "Wireless Noise-Cancelling Headphones" in result["items"][0]


def test_check_order_status_not_found():
    result = check_order_status("ORD-99999")
    assert result["found"] is False
    assert "was not found" in result["message"]


def test_get_faq_returns():
    result = get_faq("returns")
    assert result["found"] is True
    assert "30-day" in result["answer"]


def test_get_faq_unknown():
    result = get_faq("quantum physics")
    assert result["found"] is False


@pytest.mark.asyncio
async def test_create_ticket():
    await init_db()
    result = await create_ticket(
        summary="Customer received cracked screen",
        priority="HIGH",
        reason="Defective delivery",
        user_email="user@test.com"
    )
    assert result["success"] is True
    assert result["ticket_id"].startswith("TICK-")
    assert result["priority"] == "HIGH"
