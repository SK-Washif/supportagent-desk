from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    customer_id: Mapped[str] = mapped_column(
        ForeignKey("customers.customer_id", ondelete="RESTRICT"), index=True
    )
    status: Mapped[str] = mapped_column(String(64))
    estimated_delivery: Mapped[str] = mapped_column(String(64))

    customer: Mapped[Customer] = relationship(back_populates="orders")


from app.models.customer import Customer  # noqa: E402
