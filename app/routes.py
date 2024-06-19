# from datetime import timedelta
# from typing import List
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from . import crud, schemas
# from .dependencies import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_db, get_current_user
# from .models import User
# from passlib.context import CryptContext
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# app = APIRouter()

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # TOKEN
# # @router.post("/token", response_model=schemas.Token)
# # async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
# #     user = crud.get_user(db, username=form_data.username)
# #     if not user or not pwd_context.verify(form_data.password, user.hashed_password):
# #         raise HTTPException(
# #             status_code=status.HTTP_401_UNAUTHORIZED,
# #             detail="Incorrect username or password",
# #             headers={"WWW-Authenticate": "Bearer"},
# #         )
# #     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
# #     access_token = create_access_token(
# #         data={"sub": user.username}, expires_delta=access_token_expires
# #     )
# #     return {"access_token": access_token, "token_type": "bearer"}

# @app.post("/token", response_model=schemas.Token)
# async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
#     user = crud.get_user(db, form_data.username)
#     if not user or not pwd_context.verify(form_data.password, user.hashed_password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user.username}, expires_delta=access_token_expires
#     )
#     return {"access_token": access_token, "token_type": "bearer"}

# # USERS
# @app.get("/users/", response_model=List[schemas.User])
# async def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
#     users = crud.get_users(db, skip=skip, limit=limit)
#     return users

# @app.post("/users/", response_model=schemas.User)
# async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     # Verifica se o username já está cadastrado
#     db_user_by_username = crud.get_user(db, username=user.username)
#     if db_user_by_username:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    
#     # Verifica se o email já está cadastrado
#     db_user_by_email = crud.get_user_by_email(db, email=user.email)
#     if db_user_by_email:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
#     # Cria o usuário
#     return crud.create_user(db=db, user=user)

# # CLIENTS
# @app.get("/clients/", response_model=List[schemas.Client])
# async def read_clients_for_user(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     return crud.get_clients_by_owner(db=db, owner_id=current_user.id)

# @app.post("/clients/", response_model=schemas.Client)
# async def create_client_for_user(client: schemas.ClientCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     return crud.create_client(db=db, client=client, owner_id=current_user.id)
