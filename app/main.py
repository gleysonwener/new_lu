from fastapi import FastAPI, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import List, Optional
from .crud import pwd_context
from . import crud, models, schemas
from passlib.context import CryptContext
from .database import SessionLocal, engine, get_db
from .dependencies import create_access_token, get_current_active_user, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from .sentry_setup import init_sentry
from .exception_handlers import sentry_exception_handler, http_exception_handler


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

init_sentry(app)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# importing exception handlers
@app.exception_handler(Exception)
async def custom_sentry_exception_handler(request: Request, exc: Exception):
    return await sentry_exception_handler(request, exc)

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return await http_exception_handler(request, exc)


"""
    Ensuring that the first user registered with the bank is an administrator
    to give permission to other registered users
"""
def init_first_user():
    db = SessionLocal()
    try:
        existing_users = db.query(models.User).count()
        if existing_users == 0:
            first_user = schemas.UserCreate(username="admin", email="admin@example.com", password="admin")
            crud.create_user(db=db, user=first_user)
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    init_first_user()


"""
    TOKEN - Request a User Token
    Example Request:
    {
        "access_token": "string",
        "token_type": "string"
    }

    Example Response:
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtcmRpZ2l0YWwyIiwiZXhwIjoxNzE4ODI2Mjk3fQ.
        HY-acf3b6ytcILh_1Yj4RyvB2pNIx6_QAA0pjB2pTZM",
        "token_type": "bearer"
    }
"""
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user(db, username=form_data.username)
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


"""
    SESSION USER

    USER - Create a new User

    PS: ----> When the first user of the system is created, an admin user is also 
    created with an admin password to manage roles and other admin functions.
    
    Example Request:
    {
        "username": "string",
        "email": "user@example.com",
        "password": "string"
    }

    Example Response:
    {
        "id": 0,
        "username": "string",
        "email": "user@example.com",
        "role": "string"
    }

"""
@app.post("/users/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # verify if a username exits
    db_user_by_username = crud.get_user(db, username=user.username)
    if db_user_by_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    
    # Verify if an email exists
    db_user_by_email = crud.get_user_by_email(db, email=user.email)
    if db_user_by_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    return crud.create_user(db=db, user=user)


"""
    Update User Role - The user must have the role of admin and be logged in
    Example Request:
    {
        "id": 0,
        "username": "string",
        "email": "user@example.com",
        "role": "string"
    }

    Example Response:
    {
        "id": 0,
        "username": "string",
        "email": "user@example.com",
        "role": "admin"
    }
"""
@app.put("/users/{user_id}/role/", response_model=schemas.User)
async def update_user_role(
    user_id: int, new_role: str, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)
):
    updated_user = crud.update_user_role(db=db, user_id=user_id, new_role=new_role)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated_user


"""
    List all Users - User be logged in
   
    Example Response:
    [
        {
            "id": 0,
            "username": "string",
            "email": "user@example.com",
            "role": "string"
        }
    ]
"""
@app.get("/users/", response_model=List[schemas.User])
async def read_users(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return crud.get_all_users(db)


"""
    SESSION CLIENT

    Create Client - User be logged in
    Example Request:
    {
        "name": "string",
        "email": "user@example.com",
        "cpf": "string"
    }

    Example Response:
    {
        "id": 0,
        "name": "string",
        "email": "string",
        "cpf": "string",
        "owner_id": 0
    }
"""
@app.post("/clients/", response_model=schemas.Client)
async def create_client_for_user(
    client: schemas.ClientCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    try:
        return crud.create_client(db=db, client=client, owner_id=current_user.id)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))



"""
    List all clients - User be logged in

    - **skip**: Filter Number of results to skip (default: 0).
    - **limit**: Filter limit results for page (default: 10, max: 100).
    - **name**: Filter for name client (opcional).
    - **email**: Filter for email client (opcional).
    
    Example Response:
    [
        {
            "id": 0,
            "name": "string",
            "email": "string",
            "cpf": "string",
            "owner_id": 0
        }
    ]
"""
@app.get("/clients/", response_model=List[schemas.Client])
async def read_clients(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    name: str = Query(None, description="Filtrar cliente pelo nome"),
    email: str = Query(None, description="Filtrar cliente pelo email"),
    current_user: models.User = Depends(get_current_user)
):
    query = db.query(models.Client)

    if name:
        query = query.filter(models.Client.name.ilike(f"%{name}%"))
        
    if email:
        query = query.filter(models.Client.email.ilike(f"%{email}%"))

    clients = query.offset(skip).limit(limit).all()
    
    return clients



"""
    List one clients - User be logged in

    Example Request:
    {
        "id": 1,
    }
    
    Example Response:
    {
        "id": 0,
        "name": "string",
        "email": "string",
        "cpf": "string",
        "owner_id": 0
    }
"""
@app.get("/clients/{client_id}", response_model=schemas.Client)
async def get_client(client_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return client


"""
    Update client - User be logged in

    Example Request:
    {
        "id": 1,
    }
    
    Example Response:
    {
        "name": "string",
        "email": "string",
        "cpf": "string"
    }
"""
@app.put("/clients/{client_id}", response_model=schemas.Client)
def update_client(
    client_id: int, client_update: schemas.ClientUpdate, db: Session = Depends(get_db),
    
):
    updated_client = crud.update_client(db, client_id, client_update)
    if not updated_client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found or not authorized")
    return updated_client


"""
    Delete client - The user must have the role of admin and be logged in

    Example Request:
    {
        "id": 1,
    }
    
    Example Response:
    {
        "message": "Client deleted successfully"
    }
"""
@app.delete("/clients/{client_id}", response_model=dict)
async def delete_client(
    client_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)
):
    success = crud.delete_client(db, client_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found or not authorized")
    return {"message": "Client deleted successfully"}


"""
    SESSION PRODUCT

    Create products - User be logged in

    Example Request:
    {
        "description": "string",
        "sale_price": 0,
        "barcode": "string",
        "session": "string",
        "initial_stock": 0,
        "expiration_date": "2024-06-19T19:43:38.264Z",
        "images": "string",
        "available": true
    }
        
    Example Response:
    {
        "description": "string",
        "sale_price": 0,
        "barcode": "string",
        "session": "string",
        "initial_stock": 0,
        "expiration_date": "2024-06-19T19:43:38.266Z",
        "images": "string",
        "available": true,
        "id": 0
    }
"""
@app.post("/products/", response_model=schemas.Product)
def create_product(
    product: schemas.ProductCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    return crud.create_product(db=db, product=product)


"""
    List all products - User be logged in

    - **skip**: Filter Number of results to skip (default: 0).
    - **limit**: Filter limit results for page (default: 10, max: 100).
    - **description**: Filter for description of product (opcional).
    - **session**: Filter for session of product (opcional).
    - **available**: Filter for available of product (opcional).
    
    Example Response:
    [
        {
            "description": "string",
            "sale_price": 0,
            "barcode": "string",
            "session": "string",
            "initial_stock": 0,
            "expiration_date": "2024-06-19T19:39:49.321Z",
            "images": "string",
            "available": true,
            "id": 0
        }
    ]

"""
@app.get("/products/", response_model=List[schemas.Product])
async def read_products(
    skip: int = 0, 
    limit: int = 10,
    description: str = Query(None, description="Filtrar produto pelo nome"),
    session: str = Query(None, description="Filtrar produto pela sessão"),
    available: bool = Query(None, description="Filtrar por disponibilidade"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    query = db.query(models.Product)

    if description:
        query = query.filter(models.Product.description.ilike(f"%{description}%"))
        
    if session:
        query = query.filter(models.Product.session.ilike(f"%{session}%"))
    
    if available is not None:
        query = query.filter(models.Product.available == available)

    products = query.offset(skip).limit(limit).all()
    
    return products


"""
    List one products - User be logged in

    Example Request:
    {
        "id": 1
    }
        
    Example Response:
    {
        "description": "string",
        "sale_price": 0,
        "barcode": "string",
        "session": "string",
        "initial_stock": 0,
        "expiration_date": "2024-06-19T19:44:42.922Z",
        "images": "string",
        "available": true,
        "id": 0
    }
"""
@app.get("/products/{id}", response_model=schemas.Product)
def read_product(
    id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    db_product = crud.get_product(db, product_id=id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


"""
    Update product - User be logged in

    Example Request:
    {
        "id": 1
    }
        
    Example Response:
    {
        "description": "string",
        "sale_price": 0,
        "barcode": "string",
        "session": "string",
        "initial_stock": 0,
        "expiration_date": "2024-06-19T19:48:23.502Z",
        "images": "string",
        "available": true
    }
"""
@app.put("/products/{id}", response_model=schemas.Product)
def update_product(
    id: int, 
    product: schemas.ProductUpdate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    db_product = crud.get_product(db=db, product_id=id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return crud.update_product(db=db, product_id=id, product=product)


"""
    Delete product - The user must have the role of admin and be logged in

    Example Request:
    {
        "id": 1,
    }
    
    Example Response:
    {
        "message": "Product deleted successfully"
    }
"""
@app.delete("/products/{id}")
def delete_product(
    id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_active_user)
):
    db_product = crud.get_product(db=db, product_id=id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    crud.delete_product(db=db, product_id=id)
    return {"detail": "Product deleted"}


"""
    SESSION ORDER

    List all Orders - User be logged in

    - **skip**: Filter Number of results to skip (default: 0).
    - **limit**: Filter limit results for page (default: 10, max: 100).
    - **start_date**: Filter by creation date - start date - YYYY-MM-DD (opcional).
    - **end_date**: Filter by creation date - end date - YYYY-MM-DD(opcional).
    - **section**: Filter by section of product (opcional).
    - **order_id**: Filter by id id Order (opcional).
    - **status**: Filter by status Order (opcional).
    - **client_id**: Filter by id Client (opcional).
    
    Example Response:
    {
        "client_id": 0,
        "status": "string",
        "items": [
            {
            "product_id": 0,
            "quantity": 0
            }
        ]
    }
"""
@app.get("/", response_model=List[schemas.Order])
def read_orders(
    skip: int = 0,
    limit: int = 10,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    section: Optional[str] = None,
    order_id: Optional[int] = None,
    status: Optional[str] = None,
    client_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    orders = crud.get_orders(db, skip=skip, limit=limit, start_date=start_date, end_date=end_date,
        section=section, order_id=order_id, status=status, client_id=client_id
    )
    return orders


"""
    Create Order - User be logged in

    Example Request:
    {
        "client_id": 0,
        "status": "string",
        "items": [
            {
            "product_id": 0,
            "quantity": 0
            }
        ]
    }
        
    Example Response:
    {
        "client_id": 0,
        "status": "string",
        "id": 0,
        "items": [],
        "total_order_price": 0
    }
"""
@app.post("/", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_order = crud.create_order(db, order=order) # criando o pedido no bd
    db_order.update_total_order_price() # atualizando o total
    db.commit()
    db.refresh(db_order) # atualizando o objeto
    return db_order


"""
    List one Order - User be logged in

    Example Request:
    {
        "id": 1 
    }
        
    Example Response:
    {
        "client_id": 0,
        "status": "string",
        "id": 0,
        "items": [],
        "total_order_price": 0
    }
"""
@app.get("/{order_id}", response_model=schemas.Order)
def read_order(order_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_order = crud.get_order(db=db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # calc total_order_price based on orderitems
    total_price = sum(item.total_price for item in db_order.items)
    db_order.total_order_price = total_price
    
    return db_order


"""
    Update Order - User be logged in

    Example Request:
    {
        "id": 1 
    }
        
    Example Response:
    {
        "client_id": 0,
        "status": "string",
        "items": [
            {
            "product_id": 0,
            "quantity": 0
            }
        ]
    }
"""
@app.put("/{order_id}", response_model=schemas.Order)
def update_order(order_id: int, order_update: schemas.OrderUpdate, db: Session = Depends(get_db),
                 current_user: models.User = Depends(get_current_user)):
   
    db_order = crud.get_order(db=db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    if order_update.client_id:
        db_order.client_id = order_update.client_id
    if order_update.status:
        db_order.status = order_update.status

    updated_items = []

    for item_update in order_update.items:
        db_item = next((item for item in db_order.items if item.product_id == item_update.product_id), None)
        
        if db_item:
            db_item.quantity = item_update.quantity
            db_item.updated_at = datetime.utcnow()
            updated_items.append(db_item)
        else:
            new_item = schemas.OrderItemCreate(**item_update.dict(), order_id=order_id)
            db_item = crud.create_order_item(db=db, order_id=order_id, order_item=new_item)
            updated_items.append(db_item)

    items_to_remove = [item for item in db_order.items if item not in updated_items]
    for item in items_to_remove:
        db_order.items.remove(item)

    db_order.items.extend([item for item in updated_items if item not in db_order.items])

    # recalc total price order 
    db_order.update_total_order_price()
    db.commit()    
    db.refresh(db_order)

    return db_order


"""
    Delete Order - The user must have the role of admin and be logged in

    Example Request:
    {
        "id": "1",
    }
    
    Example Response:
    {
        "message": "Order deleted successfully"
    }
"""
@app.delete("/{order_id}", response_model=dict)
def delete_order(order_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    db_order = crud.delete_order(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": f"Order {order_id} deleted successfully"}
