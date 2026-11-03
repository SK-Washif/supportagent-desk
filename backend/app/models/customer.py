from __future__ import annotations

from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255))
    current_tier: Mapped[str] = mapped_column(String(32), default="Free")

    orders: Mapped[list[Order]] = relationship(back_populates="customer")
    tickets: Mapped[list[Ticket]] = relationship(back_populates="customer")

    __table_args__ = (Index("ix_customers_email", "email"),)


from app.models.order import Order  # noqa: E402
from app.models.ticket import Ticket  # noqa: E402
