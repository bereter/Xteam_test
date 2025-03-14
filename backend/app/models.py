import uuid
from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    orders: list["Order"] = Relationship(back_populates="user", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


# Many-to-many table
class ProductOrder(SQLModel, table=True):
    product_id: uuid.UUID | None = Field(default=None, foreign_key="product.id", primary_key=True, ondelete="CASCADE")
    order_id: uuid.UUID | None = Field(default=None, foreign_key="order.id", primary_key=True, ondelete="CASCADE")


# Shared properties
class ProductBase(SQLModel):
    name: str = Field(max_length=255)
    category: str = Field(max_length=255)
    prise: int = Field(gt=0)
    rating: int = Field(ge=0, le=10)


# Properties to receive via API on creation
class ProductCreate(ProductBase):
    pass


# Properties to receive on item update
class ProductUpdate(ProductBase):
    name: str | None = Field(default= None, max_length=255)
    category: str | None = Field(default= None, max_length=255)
    prise: int | None = Field(default= None, gt=0)
    rating: int | None = Field(default= None, ge=0, le=10)


# Database model, database table inferred from class name
class Product(ProductBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    orders: list["Order"] = Relationship(back_populates="products", link_model=ProductOrder)


class ProductPublic(ProductBase):
    id: uuid.UUID


# Shared properties
class OrderBase(SQLModel):
    description: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class OrderCreate(OrderBase):
    pass


# Properties to receive on item update
class OrderUpdate(OrderBase):
    pass


# Properties to return via API, id is always required
class OrderPublicAll(OrderBase):
    id: uuid.UUID


# Properties to return via API, id is always required
class OrderPublicOne(OrderBase):
    id: uuid.UUID
    products: list["Product"]


# Database model, database table inferred from class name
class Order(OrderBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    products: list["Product"] = Relationship(back_populates="orders", link_model=ProductOrder)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    user: User | None = Relationship(back_populates="orders")
