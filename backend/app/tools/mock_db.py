# Mock Orders and Products Database for NovaTech Customer Service

MOCK_ORDERS = {
    "ORD-88421": {
        "order_id": "ORD-88421",
        "customer_name": "Jordan Smith",
        "items": [
            {"name": "NovaPro Wireless Noise-Cancelling Headphones", "qty": 1, "price": 199.99},
            {"name": "AudioCare Extended Warranty (2 Years)", "qty": 1, "price": 29.99}
        ],
        "total": 229.98,
        "status": "In Transit",
        "carrier": "FedEx",
        "tracking_number": "782930192841",
        "shipped_date": "2026-11-13",
        "estimated_delivery": "2026-11-17",
        "shipping_address": "452 Market St, San Francisco, CA 94105",
        "notes": "Package handed over to carrier facility."
    },
    "ORD-10023": {
        "order_id": "ORD-10023",
        "customer_name": "Elena Rostova",
        "items": [
            {"name": "NovaPulse Ultra Mechanical Keyboard (RGB)", "qty": 1, "price": 149.00}
        ],
        "total": 149.00,
        "status": "Delivered",
        "carrier": "UPS",
        "tracking_number": "1Z9999999999999999",
        "shipped_date": "2026-11-09",
        "estimated_delivery": "2026-11-12",
        "shipping_address": "742 Evergreen Terrace, Springfield, OR 97477",
        "notes": "Delivered to front porch signature verified."
    },
    "ORD-55910": {
        "order_id": "ORD-55910",
        "customer_name": "Marcus Vance",
        "items": [
            {"name": "NovaDesk Ergonomic Sit-Stand Motorized Frame", "qty": 1, "price": 420.00}
        ],
        "total": 420.00,
        "status": "Processing",
        "carrier": "DHL Express",
        "tracking_number": "Pending Dispatched",
        "shipped_date": None,
        "estimated_delivery": "2026-11-20",
        "shipping_address": "120 Broadway, New York, NY 10271",
        "notes": "Undergoing warehouse quality inspection prior to packaging."
    }
}

MOCK_FAQ_TOPICS = {
    "returns": "We offer a 30-day money-back guarantee on all standard merchandise. Return shipping is free for defective items, or $5.99 for remorse returns. No restocking fees.",
    "shipping": "Standard shipping takes 3-5 business days ($4.99 or free over $50). Expedited is 2 business days ($12.99), and Overnight Express is $24.99.",
    "warranty": "Every NovaTech product includes a 1-year limited manufacturer warranty. Additional 2-year coverage can be added within 30 days of purchase.",
    "support_hours": "Our AI chatbot operates 24/7. Human customer support specialists are available Monday to Friday from 8:00 AM to 8:00 PM EST, and Saturday 10:00 AM to 4:00 PM EST."
}
