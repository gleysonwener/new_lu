from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from typing import List
from .crud import pwd_context
from . import crud, models, schemas
from passlib.context import CryptContext
from .database import SessionLocal, engine, get_db
from .dependencies import create_access_token, get_current_active_user, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


"""
    garantindo que o primeiro usuario cadastrado no banco seja admin
    para dar permissão aos outros usuários cadastrados
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
    TOKEN
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
    USER
"""
# cria usuario
@app.post("/users/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Verifica se o username já está cadastrado
    db_user_by_username = crud.get_user(db, username=user.username)
    if db_user_by_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    
    # Verifica se o email já está cadastrado
    db_user_by_email = crud.get_user_by_email(db, email=user.email)
    if db_user_by_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    # Cria o usuário
    return crud.create_user(db=db, user=user)


# atualiza o papel de usuario
@app.put("/users/{user_id}/role/", response_model=schemas.User)
async def update_user_role(
    user_id: int, new_role: str, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)
):
    # Atualiza o papel do usuário
    updated_user = crud.update_user_role(db=db, user_id=user_id, new_role=new_role)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated_user


# lista todos os usuário
@app.get("/users/", response_model=List[schemas.User])
async def read_users(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return crud.get_all_users(db)


"""
    CLIENT
"""
# cria cliente
@app.post("/clients/", response_model=schemas.Client)
async def create_client_for_user(
    client: schemas.ClientCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    try:
        return crud.create_client(db=db, client=client, owner_id=current_user.id)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))


# lista clientes
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


# lista unico cliente
@app.get("/clients/{client_id}", response_model=schemas.Client)
async def get_client(client_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return client

# atualiza cliente
@app.put("/clients/{client_id}", response_model=schemas.Client)
def update_client(
    client_id: int, client_update: schemas.ClientUpdate, db: Session = Depends(get_db),
    
):
    updated_client = crud.update_client(db, client_id, client_update)
    if not updated_client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found or not authorized")
    return updated_client


# exclui cliente - somente admin
@app.delete("/clients/{client_id}", response_model=dict)
async def delete_client(
    client_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)
):
    success = crud.delete_client(db, client_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found or not authorized")
    return {"message": "Client deleted successfully"}


"""
    PRODUCT
"""
# lista produtos
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

# cria produtos
@app.post("/products/", response_model=schemas.Product)
def create_product(
    product: schemas.ProductCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    return crud.create_product(db=db, product=product)

# lista um produto
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

# atualiza produto
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

# deleta um produto - somente admin
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

# """
#     ORDER
# """
# # Rota para listar todos os pedidos com filtros
# @app.get("/orders/", response_model=List[schemas.Order])
# async def read_orders(
#     skip: int = 0,
#     limit: int = 10,
#     period_start: Optional[str] = Query(None, description="Filter by start of period"),
#     period_end: Optional[str] = Query(None, description="Filter by end of period"),
#     section: Optional[str] = Query(None, description="Filter by section of products"),
#     order_id: Optional[int] = Query(None, description="Filter by order ID"),
#     status: Optional[str] = Query(None, description="Filter by order status"),
#     client_id: Optional[int] = Query(None, description="Filter by client ID"),
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user)
# ):
#     orders = crud.get_orders(db=db, skip=skip, limit=limit, period_start=period_start, period_end=period_end, section=section, order_id=order_id, status=status, client_id=client_id)
#     return orders

# # Rota para criar um novo pedido
# @app.post("/orders/", response_model=schemas.Order)
# async def create_order(
#     order: schemas.OrderCreate,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user)
# ):
#     try:
#         return crud.create_order(db=db, order=order)
#     except ValueError as ve:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

# # Rota para obter informações de um pedido específico
# @app.get("/orders/{order_id}", response_model=schemas.Order)
# async def read_order(
#     order_id: int,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user)
# ):
#     order = crud.get_order(db=db, order_id=order_id)
#     if not order:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
#     return order

# # Rota para atualizar informações de um pedido específico
# @app.put("/orders/{order_id}", response_model=schemas.Order)
# async def update_order(
#     order_id: int,
#     order_update: schemas.OrderUpdate,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user)
# ):
#     updated_order = crud.update_order(db=db, order_id=order_id, order_update=order_update)
#     if not updated_order:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
#     return updated_order

# # Rota para excluir um pedido específico
# @app.delete("/orders/{order_id}")
# async def delete_order(
#     order_id: int,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user)
# ):
#     success = crud.delete_order(db=db, order_id=order_id)
#     if not success:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
#     return {"detail": "Order deleted successfully"}