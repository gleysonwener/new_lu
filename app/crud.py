from datetime import datetime
from typing import Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


"""
    USERS
"""
def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    
    existing_users = db.query(models.User).count()
    
    role = "admin" if existing_users == 0 else "regular"
    
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password, role=role)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        return None


def update_user_role(db: Session, user_id: int, new_role: str):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.role = new_role
        db.commit()
        db.refresh(user)
    return user


def get_all_users(db: Session):
    return db.query(models.User).all()


"""
    CLIENT
"""
def get_clients_by_owner(db: Session, owner_id: int):
    return db.query(models.Client).filter(models.Client.owner_id == owner_id).all()


def get_client_by_id(db: Session, client_id: int):
    return db.query(models.Client).filter(models.Client.id == client_id).first()


# def get_client_by_id(db: Session, client_id: int, owner_id: int):
#     return db.query(models.Client).filter(models.Client.id == client_id, models.Client.owner_id == owner_id).first()


def create_client(db: Session, client: schemas.ClientCreate, owner_id: int):
    existing_client_cpf = db.query(models.Client).filter(
        models.Client.cpf == client.cpf,
        models.Client.owner_id == owner_id
    ).first()
    if existing_client_cpf:
        raise ValueError(f"Client with CPF {client.cpf} already exists for this user")
    
    existing_client_email = db.query(models.Client).filter(
        models.Client.email == client.email,
        models.Client.owner_id == owner_id
    ).first()
    if existing_client_email:
        raise ValueError(f"Client with email {client.email} already exists for this user")
    
    db_client = models.Client(**client.dict(), owner_id=owner_id)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


def update_client(db: Session, client_id: int, client_update: schemas.ClientUpdate):
    db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if db_client:
        for key, value in client_update.dict(exclude_unset=True).items():
            setattr(db_client, key, value)
        db.commit()
        db.refresh(db_client)
        return db_client
    return None


def delete_client(db: Session, client_id: int):
    db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if db_client:
        db.delete(db_client)
        db.commit()
        return True
    return False


"""
    PRODUCT
"""
def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()


def get_products(db: Session, skip: int = 0, limit: int = 10, name: str = None, session: str = None, available: bool = None):
    query = db.query(models.Product)
    if name:
        query = query.filter(models.Product.description.ilike(f"%{name}%"))
    if session:
        query = query.filter(models.Product.session.ilike(f"%{session}%"))
    if available is not None:
        query = query.filter(models.Product.available == available)
    return query.offset(skip).limit(limit).all()


def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product_id: int, product: schemas.ProductUpdate):
    db_product = get_product(db, product_id)
    if db_product:
        for key, value in product.dict(exclude_unset=True).items():
            setattr(db_product, key, value)
        db.commit()
        db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int):
    db_product = get_product(db, product_id)
    if db_product:
        db.delete(db_product)
        db.commit()
    return db_product


"""
    ORDER
"""
def get_orders(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    section: Optional[str] = None,
    order_id: Optional[int] = None,
    status: Optional[str] = None,
    client_id: Optional[int] = None
):
    query = db.query(models.Order)

    if start_date:
        query = query.filter(models.Order.created_at >= start_date)
    if end_date:
        query = query.filter(models.Order.created_at <= end_date)
    if section:
        query = query.join(models.Order.items).join(models.OrderItem.product).filter(models.Product.session == section)
    if order_id:
        query = query.filter(models.Order.id == order_id)
    if status:
        query = query.filter(models.Order.status == status)
    if client_id:
        query = query.filter(models.Order.client_id == client_id)

    query = query.order_by(models.Order.id.asc())

    query = query.offset(skip).limit(limit)

    return query.all()


def get_order(db: Session, order_id: int):
    return db.query(models.Order).filter(models.Order.id == order_id).first()


def create_order(db: Session, order: schemas.OrderCreate):
    db_order = models.Order(client_id=order.client_id, status="pending")
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # add items order
    for item in order.items:
        product = db.query(models.Product).get(item.product_id)
        subtotal = item.quantity * product.sale_price

        if product.initial_stock < item.quantity:
            raise ValueError(f"Not enough stock available for product with id {item.product_id}")

        db_item = models.OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            subtotal=subtotal,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(db_item)
    product.initial_stock -= item.quantity
    db.commit()

    db.refresh(db_order)
    return db_order


def update_order(db: Session, order_id: int, order_update: schemas.OrderUpdate):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if db_order:
        if order_update.client_id:
            db_order.client_id = order_update.client_id
        if order_update.status:
            db_order.status = order_update.status
        
        if order_update.items:
            for item_update in order_update.items:
                db_item = db.query(models.OrderItem).filter(
                    models.OrderItem.product_id == item_update.product_id,
                    models.OrderItem.order_id == order_id
                ).first()
                if db_item:
                    db_item.quantity = item_update.quantity
                    db_item.updated_at = datetime.utcnow()
        
        db_order.update_total_order_price()
        db.commit()
        db.refresh(db_order)
    return db_order


def delete_order(db: Session, order_id: int) -> Optional[schemas.Order]:
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if db_order:
        db.delete(db_order)
        db.commit()
        return db_order
    return None
