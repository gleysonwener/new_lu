from typing import Optional
from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

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


