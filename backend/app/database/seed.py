"""Idempotent seed data: 9 tickets, 5 customers, 3 orders."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Customer, Order, Ticket

CUSTOMERS = [
    {"customer_id": "USR-101", "name": "Amelia Hart", "email": "amelia.hart@example.com", "current_tier": "Pro"},
    {"customer_id": "USR-204", "name": "Daniel Okafor", "email": "daniel.okafor@example.com", "current_tier": "Free"},
    {"customer_id": "USR-309", "name": "Priya Nair", "email": "priya.nair@example.com", "current_tier": "Free"},
    {"customer_id": "USR-410", "name": "Marcus Chen", "email": "marcus.chen@example.com", "current_tier": "Enterprise"},
    {"customer_id": "USR-511", "name": "Sofia Reyes", "email": "sofia.reyes@example.com", "current_tier": "Pro"},
]

ORDERS = [
    {"order_id": "ORD-9012", "customer_id": "USR-101", "status": "In Transit", "estimated_delivery": "Tomorrow"},
    {"order_id": "ORD-8845", "customer_id": "USR-410", "status": "Delivered", "estimated_delivery": "Today"},
    {"order_id": "ORD-7723", "customer_id": "USR-511", "status": "Processing", "estimated_delivery": "In 3 days"},
]

TICKETS = [
    # --- Original 3 (assignment) ---
    {
        "ticket_id": "TCK-001",
        "customer_id": "USR-101",
        "order_id": "ORD-9012",
        "subject": "Where is my package?",
        "message": "Where is my package #ORD-9012? It was supposed to arrive yesterday.",
    },
    {
        "ticket_id": "TCK-002",
        "customer_id": "USR-204",
        "order_id": None,
        "subject": "Enterprise tier upgrade",
        "message": "Can you upgrade my account to Enterprise tier?",
    },
    {
        "ticket_id": "TCK-003",
        "customer_id": "USR-309",
        "order_id": None,
        "subject": "Update profile picture",
        "message": "How do I update my profile picture?",
    },
    # --- Extra 6 (variety: tool, no-tool, escalation, identity-check) ---
    {
        "ticket_id": "TCK-004",
        "customer_id": "USR-410",
        "order_id": "ORD-8845",
        "subject": "Order arrived damaged",
        "message": "My order ORD-8845 just arrived but the box was crushed. "
                   "I need a replacement — what is the status of the shipment?",
    },
    {
        "ticket_id": "TCK-005",
        "customer_id": "USR-511",
        "order_id": "ORD-7723",
        "subject": "Change delivery address",
        "message": "Can I change the delivery address for ORD-7723? "
                   "I am moving this weekend and want to make sure it arrives.",
    },
    {
        "ticket_id": "TCK-006",
        "customer_id": "USR-204",
        "order_id": None,
        "subject": "Reset password",
        "message": "I forgot my password and I cannot log in. How do I reset it?",
    },
    {
        "ticket_id": "TCK-007",
        "customer_id": "USR-309",
        "order_id": None,
        "subject": "Do you offer SSO?",
        "message": "We are evaluating your product for our team. "
                   "Do you support SAML / SSO sign-in?",
    },
    {
        "ticket_id": "TCK-008",
        "customer_id": "USR-410",
        "order_id": "ORD-8845",
        "subject": "Talk to someone about pricing",
        "message": "I want to discuss our contract and per-seat pricing for next year. "
                   "Who can I talk to?",
    },
    {
        "ticket_id": "TCK-009",
        "customer_id": "USR-511",
        "order_id": None,
        "subject": "Where is my order?",
        "message": "Where is my order? I have not received it yet.",
    },
]


def seed_database(db: Session) -> None:
    """Insert missing seed rows only; safe to run on every startup."""
    for row in CUSTOMERS:
        if db.scalar(select(Customer).where(Customer.customer_id == row["customer_id"])) is None:
            db.add(Customer(**row))
    db.flush()

    for row in ORDERS:
        if db.scalar(select(Order).where(Order.order_id == row["order_id"])) is None:
            db.add(Order(**row))
    db.flush()

    for row in TICKETS:
        if db.scalar(select(Ticket).where(Ticket.ticket_id == row["ticket_id"])) is None:
            db.add(Ticket(**row))
    db.commit()