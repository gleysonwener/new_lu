from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, Numeric, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="regular")

    clients = relationship("Client", back_populates="owner")
    products = relationship("Product", back_populates="owner")

class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    email = Column(String, index=True)
    cpf = Column(String, index=True)
    
    owner = relationship("User", back_populates="clients")
    orders = relationship("Order", back_populates="client")

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    sale_price = Column(Float, nullable=False)
    barcode = Column(String, unique=True, index=True)
    session = Column(String, index=True)
    initial_stock = Column(Integer, nullable=False)
    expiration_date = Column(DateTime, nullable=True)
    images = Column(String, nullable=True)  # This will store image URLs or paths
    available = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship("User", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
    



# class Order(Base):
#     __tablename__ = "orders"

#     id = Column(Integer, primary_key=True, index=True)
#     client_id = Column(Integer, ForeignKey("clients.id"))
#     status = Column(String)
#     total_order_price = Column(Numeric(10, 2), default=0.0)
    
#     client = relationship("Client", back_populates="orders")
#     items = relationship("OrderItem", back_populates="order")

#     # calc total price order
#     def update_total_order_price(self):
#         total = sum(item.total_price for item in self.items)
#         self.total_order_price = total

#     def as_dict(self):
#         return {
#             "id": self.id,
#             "client_id": self.client_id,
#             "status": self.status,
#             "total_order_price": float(self.total_order_price),
#             "items": [item.as_dict() for item in self.items]
#         }

# class OrderItem(Base):
#     __tablename__ = "order_items"

#     id = Column(Integer, primary_key=True, index=True)
#     order_id = Column(Integer, ForeignKey("orders.id"))
#     product_id = Column(Integer, ForeignKey("products.id"))
#     quantity = Column(Integer)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

#     order = relationship("Order", back_populates="items")
#     product = relationship("Product")

#     @property
#     def total_price(self):
#         return self.quantity * self.product.sale_value

#     def as_dict(self):
#         return {
#             "id": self.id,
#             "order_id": self.order_id,
#             "product_id": self.product_id,
#             "quantity": self.quantity,
#             "total_price": self.total_price,
#             "created_at": self.created_at,
#         }