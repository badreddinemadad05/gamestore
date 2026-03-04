# =================================
# Models - Définition des tables
# =================================

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

# ================================
# Modèle User (Table des utilisateurs)
# ================================
class User(SQLModel, table=True):
    """Modèle pour la table des utilisateurs
    
    Attributs:
        id (int): Identifiant unique auto-incrémenté
        email (str): Email de l'utilisateur (unique)
        username (str): Nom d'utilisateur
        hashed_password (str): Mot de passe hashé avec bcrypt
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    username: str
    hashed_password: str
    orders: List['Order'] = Relationship(back_populates='user')

# ================================
# Modèle Contact (Table des messages)
# ================================
class Contact(SQLModel, table=True):
    """Modèle pour la table des messages de contact
    
    Attributs:
        id (int): Identifiant unique auto-incrémenté
        name (str): Nom de l'expéditeur
        email (str): Email de l'expéditeur
        subject (str): Sujet du message
        message (str): Contenu du message
        date_sent (datetime): Date d'envoi (auto)
        is_read (bool): Statut de lecture (false par défaut)
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    subject: str
    message: str
    date_sent: datetime = Field(default_factory=datetime.now)
    is_read: bool = Field(default=False)

class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key='user.id')
    order_date: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default='pending')  # pending, completed, cancelled
    total_amount: float
    shipping_address: str
    shipping_city: str
    shipping_postal_code: str
    shipping_country: str = Field(default='France')
    phone_number: str
    special_instructions: Optional[str] = None
    
    # Relations
    user: Optional[User] = Relationship(back_populates='orders')
    items: List['OrderItem'] = Relationship(back_populates='order')

class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key='order.id')
    product_name: str
    product_price: float
    quantity: int
    product_image: str
    
    # Relations
    order: Order = Relationship(back_populates='items')