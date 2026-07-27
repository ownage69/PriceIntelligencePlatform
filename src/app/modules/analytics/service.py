from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.prices.models import PriceHistory
from app.shared.utils.math import calculate_percentage_change


class PriceAnalyticsService:

    async def get_product_price_dynamics(self, session: AsyncSession, product_id: int) -> dict[str, Any]:
        stats_stmt = select(
            func.min(PriceHistory.price).label("min_price"),
            func.max(PriceHistory.price).label("max_price"),
            func.avg(PriceHistory.price).label("avg_price")
        ).where(PriceHistory.product_id == product_id)
        
        stats_result = await session.execute(stats_stmt)
        stats = stats_result.first()

        history_stmt = (
            select(PriceHistory.price)
            .where(PriceHistory.product_id == product_id)
            .order_by(PriceHistory.collected_at.asc())
        )
        history_result = await session.execute(history_stmt)
        prices = history_result.scalars().all()

        if not prices:
            return {}

        first_price = prices[0]
        current_price = prices[-1]
        percentage_change = calculate_percentage_change(first_price, current_price)

        return {
            "current_price": current_price,
            "min_price": stats.min_price,
            "max_price": stats.max_price,
            "avg_price": round(stats.avg_price, 2) if stats.avg_price else None,
            "total_change_percent": percentage_change
        }


analytics_service = PriceAnalyticsService()
