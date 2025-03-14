from fastapi import APIRouter, HTTPException
from sqlmodel import select, desc

from app.api.deps import CurrentUser, SessionDep
from app.models import Product, Order

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/")
def recommendations_users(
        session: SessionDep,
        current_user: CurrentUser
) -> list:
    """
    Recommendations for users
    """
    query = (
        select(Order)
        .filter_by(user_id=current_user.id)
        .offset(0)
        .limit(20)
    )
    recommendations_order = session.exec(query).all()[-1]
    products = [i for i in recommendations_order.products]
    return products
