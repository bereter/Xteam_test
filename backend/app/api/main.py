from fastapi import APIRouter

from app.api.routes import items, login, private, users, utils, products, orders, recommendations
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(products.router)
api_router.include_router(orders.router)
api_router.include_router(recommendations.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
