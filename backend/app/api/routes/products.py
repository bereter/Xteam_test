import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import Product, ProductCreate, ProductUpdate, ProductPublic, Message

router = APIRouter(prefix="/products", tags=["product"])


@router.get("/", response_model=list[ProductPublic])
def read_products(
        session: SessionDep,
        category: str | None = None,
        limit: int = 10,
        offset: int = 0
) -> Any:
    """
    Retrieve products.
    """
    if category:
        query = (
            select(Product)
            .filter_by(category=category)
            .order_by(Product.rating)
            .offset(offset)
            .limit(limit)
        )
    else:
        query = (
            select(Product)
            .order_by(Product.rating)
            .offset(offset)
            .limit(limit)
        )
    result = session.execute(query)
    products = result.scalars().all()
    return products


@router.get("/{id}", response_model=ProductPublic)
def read_product(session: SessionDep, id: uuid.UUID) -> Any:
    """
    Get product by ID.
    """
    product = session.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post('/', response_model=ProductPublic)
def create_product(
        session: SessionDep,
        product_in: ProductCreate,
        current_user: CurrentUser
) -> Any:
    """
    Crate new product
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    product = Product.model_validate(product_in)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.put("/{id}", response_model=ProductPublic)
def update_product(
        session: SessionDep,
        id: uuid.UUID,
        product_in: ProductUpdate,
        current_user: CurrentUser
) -> Any:
    """
    Update an product.
    """
    product = session.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = product_in.model_dump(exclude_unset=True)
    product.sqlmodel_update(update_dict)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.delete("/{id}")
def delete_product(
        session: SessionDep,
        id: uuid.UUID,
        current_user: CurrentUser
) -> Message:
    """
    Delete an product
    """
    product = session.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(product)
    session.commit()
    return Message(message="Product deleted successfully")