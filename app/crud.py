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


def get_client_by_id(db: Session, client_id: int):
    return db.query(models.Client).filter(models.Client.id == client_id).first()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    
    # Verifica se existem usuários no banco de dados
    existing_users = db.query(models.User).count()
    
    # Define o papel como admin se não houver usuários
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
# lista cliente pelo dono
def get_clients_by_owner(db: Session, owner_id: int):
    return db.query(models.Client).filter(models.Client.owner_id == owner_id).all()


# lista cliente pelo id
def get_client_by_id(db: Session, client_id: int, owner_id: int):
    return db.query(models.Client).filter(models.Client.id == client_id, models.Client.owner_id == owner_id).first()


# cria cliente
def create_client(db: Session, client: schemas.ClientCreate, owner_id: int):
    # Verifica se já existe um cliente com o mesmo CPF para o mesmo dono
    existing_client_cpf = db.query(models.Client).filter(
        models.Client.cpf == client.cpf,
        models.Client.owner_id == owner_id
    ).first()
    if existing_client_cpf:
        raise ValueError(f"Client with CPF {client.cpf} already exists for this user")
    
    # Verifica se já existe um cliente com o mesmo email para o mesmo dono
    existing_client_email = db.query(models.Client).filter(
        models.Client.email == client.email,
        models.Client.owner_id == owner_id
    ).first()
    if existing_client_email:
        raise ValueError(f"Client with email {client.email} already exists for this user")
    
    # Cria um novo cliente caso não exista um cliente com o mesmo CPF ou email
    db_client = models.Client(**client.dict(), owner_id=owner_id)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


# atualiza cliente
def update_client(db: Session, client_id: int, client_update: schemas.ClientUpdate, owner_id: int):
    db_client = db.query(models.Client).filter(models.Client.id == client_id, models.Client.owner_id == owner_id).first()
    if db_client:
        for key, value in client_update.dict(exclude_unset=True).items():
            setattr(db_client, key, value)
        db.commit()
        db.refresh(db_client)
        return db_client
    return None


# deleta cliente
def delete_client(db: Session, client_id: int, owner_id: int):
    db_client = db.query(models.Client).filter(models.Client.id == client_id, models.Client.owner_id == owner_id).first()
    if db_client:
        db.delete(db_client)
        db.commit()
        return True
    return False
