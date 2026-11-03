from __future__ import annotations

from typing import Any

from sqlalchemy import select

from app.core.exceptions import ToolError
from app.models import Customer
from app.tools.definitions import GetUserTierArgs, ToolContext

TOP_TIER = "Enterprise"


def get_user_tier(ctx: ToolContext, args: GetUserTierArgs) -> dict[str, Any]:
    customer = ctx.db.scalar(select(Customer).where(Customer.customer_id == args.user_id))
    if customer is None:
        raise ToolError("customer_not_found", f"No customer exists with id {args.user_id}.")
    if customer.customer_id != ctx.customer_id:
        raise ToolError(
            "customer_not_accessible",
            f"Customer {args.user_id} is not the customer who opened this ticket.",
        )
    return {
        "user_id": customer.customer_id,
        "current_tier": customer.current_tier,
        "eligible_for_upgrade": customer.current_tier != TOP_TIER,
    }
