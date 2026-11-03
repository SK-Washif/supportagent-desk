from __future__ import annotations

from typing import Any

from sqlalchemy import select

from app.core.exceptions import ToolError
from app.models import Order
from app.tools.definitions import GetOrderStatusArgs, ToolContext


def get_order_status(ctx: ToolContext, args: GetOrderStatusArgs) -> dict[str, Any]:
    order = ctx.db.scalar(select(Order).where(Order.order_id == args.order_id))
    if order is None:
        raise ToolError("order_not_found", f"No order exists with id {args.order_id}.")
    if order.customer_id != ctx.customer_id:
        # The model must not read other customers' data, even if a ticket asks it to.
        raise ToolError(
            "order_not_accessible",
            f"Order {args.order_id} does not belong to the customer who opened this ticket.",
        )
    return {
        "order_id": order.order_id,
        "status": order.status,
        "est_delivery": order.estimated_delivery,
    }
