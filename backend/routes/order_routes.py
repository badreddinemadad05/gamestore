# =================================
# Routes de gestion des commandes
# =================================

from fastapi import APIRouter, HTTPException, Request
from typing import List
from pydantic import BaseModel
from database import get_db

# Création du routeur
router = APIRouter()

# ================================
# Documentation des routes
# ================================
"""Ce module gère toutes les routes liées aux commandes :

Routes disponibles:
    POST /orders : Création d'une nouvelle commande
    GET /orders : Récupération de toutes les commandes
    GET /orders/{order_id} : Détails d'une commande
    PUT /orders/{order_id}/status : Mise à jour du statut
"""

# Définition des modèles de données
class OrderItemCreate(BaseModel):
    product_name: str
    product_price: float
    quantity: int
    product_image: str

class OrderCreate(BaseModel):
    user_id: int
    total_amount: float
    shipping_address: str
    shipping_city: str
    shipping_postal_code: str
    phone_number: str
    special_instructions: str = None
    items: List[OrderItemCreate]

# ================================
# Route de création de commande
# ================================
@router.post("/orders")
def create_order(order_data: OrderCreate):
    """Crée une nouvelle commande (sqlite3 natif)"""
    with get_db() as conn:
        # Vérifier si l'utilisateur existe
        user = conn.execute("SELECT * FROM users WHERE id = ?", (order_data.user_id,)).fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        # Créer la commande
        cur = conn.execute(
            """
            INSERT INTO orders (user_id, total_amount, shipping_address, shipping_city, shipping_postal_code, phone_number, special_instructions, order_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), 'pending')
            """,
            (
                order_data.user_id,
                order_data.total_amount,
                order_data.shipping_address,
                order_data.shipping_city,
                order_data.shipping_postal_code,
                order_data.phone_number,
                order_data.special_instructions
            )
        )
        order_id = cur.lastrowid
        # Ajouter les articles de la commande
        for item in order_data.items:
            conn.execute(
                """
                INSERT INTO order_items (order_id, product_name, product_price, quantity, product_image)
                VALUES (?, ?, ?, ?, ?)
                """,
                (order_id, item.product_name, item.product_price, item.quantity, item.product_image)
            )
        conn.commit()
        return {"message": "Commande créée avec succès", "order_id": order_id}

# ================================
# Route de récupération des commandes
# ================================
@router.get("/orders")
def get_all_orders():
    """Récupère toutes les commandes (sqlite3 natif)"""
    with get_db() as conn:
        orders = conn.execute("SELECT * FROM orders ORDER BY order_date DESC").fetchall()
        result = []
        for order in orders:
            items = conn.execute("SELECT * FROM order_items WHERE order_id = ?", (order["id"],)).fetchall()
            user = conn.execute("SELECT * FROM users WHERE id = ?", (order["user_id"],)).fetchone()
            order_dict = {
                "id": order["id"],
                "user_name": user["username"] if user else "Utilisateur supprimé",
                "user_email": user["email"] if user else "Email non disponible",
                "date": order["order_date"],
                "status": order["status"],
                "total_amount": order["total_amount"],
                "shipping_address": order["shipping_address"],
                "shipping_city": order["shipping_city"],
                "shipping_postal_code": order["shipping_postal_code"],
                "phone": order["phone_number"],
                "special_instructions": order["special_instructions"],
                "items": [
                    {
                        "name": item["product_name"],
                        "price": item["product_price"],
                        "quantity": item["quantity"],
                        "image": item["product_image"]
                    }
                    for item in items
                ]
            }
            result.append(order_dict)
        return result

# ================================
# Route de détail d'une commande
# ================================
@router.get("/orders/{order_id}")
def get_order(order_id: int, request: Request):
    """Récupère les détails d'une commande (sqlite3 natif, sécurisé)"""
    with get_db() as conn:
        order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
        if not order:
            raise HTTPException(status_code=404, detail="Commande non trouvée")
        # Vérifie que l'utilisateur connecté est bien le propriétaire
        user_id = getattr(request.state, "user_id", None)
        if user_id is None or user_id != order["user_id"]:
            raise HTTPException(status_code=403, detail="Accès refusé : cette commande n'appartient pas à l'utilisateur.")
        items = conn.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,)).fetchall()
        user = conn.execute("SELECT * FROM users WHERE id = ?", (order["user_id"],)).fetchone()
        return {
            "id": order["id"],
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"]
            } if user else None,
            "order_date": order["order_date"],
            "status": order["status"],
            "total_amount": order["total_amount"],
            "shipping_address": order["shipping_address"],
            "shipping_city": order["shipping_city"],
            "shipping_postal_code": order["shipping_postal_code"],
            "phone_number": order["phone_number"],
            "special_instructions": order["special_instructions"],
            "items": [
                {
                    "product_name": item["product_name"],
                    "product_price": item["product_price"],
                    "quantity": item["quantity"],
                    "product_image": item["product_image"]
                }
                for item in items
            ]
        }

# ================================
# Route de mise à jour du statut
# ================================
@router.patch("/orders/{order_id}/status")
def update_order_status(order_id: int, status: str):
    """Met à jour le statut d'une commande (sqlite3 natif)"""
    with get_db() as conn:
        order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
        if not order:
            raise HTTPException(status_code=404, detail="Commande non trouvée")
        if status not in ["pending", "completed", "cancelled"]:
            raise HTTPException(status_code=400, detail="Statut invalide")
        conn.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
        conn.commit()
        return {"message": "Statut de la commande mis à jour", "status": status}

@router.get("/users/{user_id}/orders")
def get_user_orders(user_id: int):
    """Récupère toutes les commandes d'un utilisateur (sqlite3 natif)"""
    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        orders = conn.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY order_date DESC", (user_id,)).fetchall()
        result = []
        for order in orders:
            items = conn.execute("SELECT * FROM order_items WHERE order_id = ?", (order["id"],)).fetchall()
            order_dict = {
                "id": order["id"],
                "order_date": order["order_date"],
                "status": order["status"],
                "total_amount": order["total_amount"],
                "shipping_address": order["shipping_address"],
                "shipping_city": order["shipping_city"],
                "shipping_postal_code": order["shipping_postal_code"],
                "phone_number": order["phone_number"],
                "special_instructions": order["special_instructions"],
                "items": [
                    {
                        "product_name": item["product_name"],
                        "product_price": item["product_price"],
                        "quantity": item["quantity"],
                        "product_image": item["product_image"]
                    }
                    for item in items
                ]
            }
            result.append(order_dict)
        return result


@router.delete("/orders/{order_id}")
def delete_order(order_id: int):
    """Supprime une commande et ses articles (sqlite3 natif)"""
    with get_db() as conn:
        order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
        if not order:
            raise HTTPException(status_code=404, detail="Commande non trouvÃ©e")

        conn.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))
        conn.execute("DELETE FROM orders WHERE id = ?", (order_id,))
        conn.commit()
        return {"message": "Commande supprimÃ©e"}
