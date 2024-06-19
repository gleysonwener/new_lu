from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr


# TOKEN
class Token(BaseModel):
    access_token: str
    token_type: str


# USER
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserRole(BaseModel):
    role: str  # Pode ser 'admin' ou 'regular'

class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str

    class Config:
        orm_mode = True


# CLIENT
class ClientBase(BaseModel):
    name: str
    email: EmailStr
    cpf: str

class ClientCreate(ClientBase):
    pass

class ClientDelete(BaseModel):
    client_id: int

class Client(BaseModel):
    id: int
    name: str
    email: str
    cpf: str
    owner_id: int

    class Config:
        orm_mode = True

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    cpf: Optional[str] = None


# PRODUCT
class ProductBase(BaseModel):
    description: Optional[str] = None
    sale_price: Optional[float] = None
    barcode: Optional[str] = None
    session: Optional[str] = None
    initial_stock: Optional[int] = None
    expiration_date: Optional[datetime] = None
    images: Optional[str] = None
    available: Optional[bool] = None

class ProductCreate(ProductBase):
    description: str
    sale_price: float
    barcode: str
    session: str
    initial_stock: int

class ProductUpdate(ProductBase):
    pass

class Product(ProductBase):
    id: int

    class Config:
        orm_mode = True

# ORDER ITEM

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemUpdate(OrderItemBase):
    quantity: Optional[int]

class OrderItem(OrderItemBase):
    id: int
    subtotal: float

    class Config:
        orm_mode = True

# ORDER
# class OrderBase(BaseModel):
#     client_id: int

# class OrderCreate(OrderBase):
#     items: List[OrderItemCreate]

# class OrderUpdate(BaseModel):
#     status: str

# class Order(OrderBase):
#     id: int
#     items: List[OrderItem] = []
#     status: str
#     subtotal: Optional[float]
#     total: Optional[float]

#     class Config:
#         orm_mode = True

# ######
# class OrderItemBase(BaseModel):
#     product_id: int
#     quantity: int

# class OrderItemCreate(OrderItemBase):
#     pass

# class OrderItemUpdate(OrderItemBase):
#     quantity: Optional[int]

# class OrderItem(OrderItemBase):
#     id: int
#     subtotal: float

#     class Config:
#         orm_mode = True

# class OrderBase(BaseModel):
#     client_id: int

# class OrderCreate(OrderBase):
#     items: List[OrderItemCreate]

# class OrderUpdate(BaseModel):
#     status: str

# class Order(OrderBase):
#     id: int
#     items: List[OrderItem] = []
#     status: str
#     subtotal: Optional[float]
#     total: Optional[float]

#     def calculate_subtotal(self):
#         self.subtotal = sum(item.subtotal for item in self.items)
    
#     def calculate_total(self):
#         self.total = self.subtotal  # Adicione lógica de cálculo de impostos, descontos, etc., se necessário

#     class Config:
#         orm_mode = True