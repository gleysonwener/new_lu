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
async def read_clients_for_user(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    name: str = Query(None, description="Filtrar cliente pelo nome"),
    email: str = Query(None, description="Filtrar cliente pelo email"),
):
    query = db.query(models.Client).filter(models.Client.owner_id == current_user.id)

    if name:
        query = query.filter(models.Client.name.ilike(f"%{name}%"))
        
    if email:
        query = query.filter(models.Client.email.ilike(f"%{email}%"))

    clients = query.offset(skip).limit(limit).all()
    
    return clients


# lista unico cliente
@app.get("/clients/{client_id}", response_model=schemas.Client)
async def get_client(client_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    client = crud.get_client_by_id(db, client_id, current_user.id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found or not authorized")
    return client   


# atualiza cliente
@app.put("/clients/{client_id}", response_model=schemas.Client)
def update_client(
    client_id: int, client_update: schemas.ClientUpdate, db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    updated_client = crud.update_client(db, client_id, client_update, current_user.id)
    if not updated_client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found or not authorized")
    return updated_client


# exclui cliente
@app.delete("/clients/{client_id}", response_model=dict)
async def delete_client(
    client_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete clients",
        )
    success = crud.delete_client(db, client_id, current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found or not authorized")
    return {"message": "Client deleted successfully"}

