"""Telegram handlers grouped by feature."""

from handlers.categories import category_router
from handlers.common import common_router
from handlers.transactions import transaction_router

routers = (
    common_router,
    transaction_router,
    category_router,
)

__all__ = ["routers"]
