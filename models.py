"""
Pydantic models for data validation
"""
from pydantic import BaseModel


# User Models
class UserRegister(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: str
    username: str


# Product Models
class Product(BaseModel):
    name: str
    price: float


class ProductResponse(BaseModel):
    _id: str
    name: str
    price: float
