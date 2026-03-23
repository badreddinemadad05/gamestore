from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    email: str
    username: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class ContactCreate(BaseModel):
    name: str
    email: str
    subject: str
    message: str

class OrderItemCreate(BaseModel):
    product_name: str
    product_price: float
    quantity: int
    product_image: str

class OrderCreate(BaseModel):
    shipping_address: str
    shipping_city: str
    shipping_postal_code: str
    phone_number: str
    special_instructions: Optional[str] = None
    items: List[OrderItemCreate]
