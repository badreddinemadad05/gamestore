# =================================
# Routes de gestion des messages de contact
# =================================
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_db

# Création du routeur
router = APIRouter()

# ================================
# Documentation des routes
# ================================
"""Ce module gère toutes les routes liées aux messages de contact :

Routes disponibles:
    POST /contact : Création d'un nouveau message
    GET /contact : Récupération de tous les messages
    PUT /contact/{contact_id}/read : Marquer un message comme lu
"""

class ContactCreate(BaseModel):
    name: str
    email: str
    subject: str
    message: str

@router.post("/contact")
def create_contact(contact_data: ContactCreate):
    """Crée un nouveau message de contact (sqlite3 natif)"""
    with get_db() as conn:
        cur = conn.execute(
            """
            INSERT INTO contacts (name, email, subject, message, date_sent, is_read)
            VALUES (?, ?, ?, ?, datetime('now'), 0)
            """,
            (contact_data.name, contact_data.email, contact_data.subject, contact_data.message)
        )
        contact_id = cur.lastrowid
        conn.commit()
        
        contact = conn.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,)).fetchone()
        return {
            "message": "Message reçu !",
            "id": contact["id"],
            "name": contact["name"],
            "email": contact["email"],
            "subject": contact["subject"],
            "date_sent": contact["date_sent"]
        }

@router.get("/contact")
def get_all_contacts():
    """Récupère tous les messages de contact (sqlite3 natif)"""
    with get_db() as conn:
        contacts = conn.execute("SELECT * FROM contacts ORDER BY date_sent DESC").fetchall()
        return [
            {
                "id": c["id"],
                "name": c["name"],
                "email": c["email"],
                "subject": c["subject"],
                "message": c["message"],
                "date_sent": c["date_sent"],
                "is_read": bool(c["is_read"])
            }
            for c in contacts
        ]

@router.put("/contact/{contact_id}/read")
def mark_as_read(contact_id: int):
    """Marque un message comme lu (sqlite3 natif)"""
    with get_db() as conn:
        contact = conn.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,)).fetchone()
        if not contact:
            raise HTTPException(status_code=404, detail="Message non trouvé")
        
        conn.execute("UPDATE contacts SET is_read = 1 WHERE id = ?", (contact_id,))
        conn.commit()
        return {"message": "Message marqué comme lu"}
@router.delete("/contact/{contact_id}")
def delete_contact(contact_id: int):
    """Supprime un message de contact (sqlite3 natif)"""
    with get_db() as conn:
        contact = conn.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,)).fetchone()
        if not contact:
            raise HTTPException(status_code=404, detail="Message non trouve")
        conn.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
        conn.commit()
        return {"message": "Message supprime"}
