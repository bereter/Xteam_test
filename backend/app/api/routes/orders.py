import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import Order, OrderCreate, OrderPublicOne, OrderUpdate, Message, OrderPublicAll, Product

router = APIRouter(prefix="/orders", tags=["order"])


@router.get("/", response_model=list[OrderPublicAll])
def read_orders(
        session: SessionDep,
        current_user: CurrentUser,
        limit: int = 10,
        offset: int = 0
) -> Any:
    """
    Retrieve a user's order.
    """
    query = (
        select(Order)
        .filter_by(user_id=current_user.id)
        .offset(offset)
        .limit(limit)
    )
    result = session.execute(query)
    order = result.scalars().all()
    return order


@router.get("/{id}", response_model=OrderPublicOne)
def read_order(session: SessionDep, id: uuid.UUID, current_user: CurrentUser) -> Any:
    """
    Get a user's order by ID.
    """
    order = session.get(Order, id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if not current_user.is_superuser and (order.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return order


@router.post('/', response_model=OrderPublicOne)
def create_order(
        session: SessionDep,
        order_in: OrderCreate,
        current_user: CurrentUser,
        products_list: list[uuid.UUID]
) -> Any:
    """
    Crate new order
    """
    products_list = [session.get(Product, product_id) for product_id in products_list]
    order = Order.model_validate(order_in, update={"user_id": current_user.id, "products": products_list})
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


# @router.put("/{id}", response_model=OrderPublicOne)
# def update_order(
#     session: SessionDep,
#     current_user: CurrentUser,
#     id: uuid.UUID,
#     order_in: OrderUpdate,
# ) -> Any:
#     """
#     Update an order.
#     """
#     order = session.get(Order, id)
#     if not order:
#         raise HTTPException(status_code=404, detail="Order not found")
#     if not current_user.is_superuser and (order.user_id != current_user.id):
#         raise HTTPException(status_code=400, detail="Not enough permissions")
#     update_dict = order_in.model_dump(exclude_unset=True)
#     order.sqlmodel_update(update_dict)
#     session.add(order)
#     session.commit()
#     session.refresh(order)
#     return order


@router.delete("/{id}")
def delete_order(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an order.
    """
    order = session.get(Order, id)
    if not order:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (order.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(order)
    session.commit()
    return Message(message="Order deleted successfully")