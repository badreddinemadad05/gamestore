from fastapi import APIRouter, Depends, HTTPException, Request
from database import add_user, get_user_by_email
from models import User, Order, OrderItem
from auth import hash_password, verify_password, create_access_token
from datetime import datetime, timedelta
import bcrypt
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

# =================================
# Routes d'authentification
# =================================

# Création du routeur
router = APIRouter()

# Utiliser la même clé et algorithme que dans auth.py
from auth import SECRET_KEY as AUTH_SECRET_KEY, ALGORITHM as AUTH_ALGORITHM

SECRET_KEY = AUTH_SECRET_KEY
ALGORITHM = AUTH_ALGORITHM
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")

from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    password: str  # Le mot de passe en clair qui sera haché

# ================================
# Documentation des routes
# ================================
"""Ce module gère toutes les routes liées à l'authentification :

Routes disponibles:
    POST /register : Inscription d'un nouvel utilisateur
    POST /login : Connexion d'un utilisateur
    GET /users : Liste de tous les utilisateurs (admin)
    DELETE /users/{user_id} : Suppression d'un utilisateur
"""

# ================================
# Route d'inscription
# ================================
@router.post("/register")
def register(user_data: UserCreate):
    """Inscription d'un nouvel utilisateur (sqlite3 natif)
    
    Paramètres:
        user_data (UserCreate): Données de l'utilisateur (email, username, password)
    
    Retourne:
        dict: Message de confirmation
    
    Lève:
        HTTPException(400): Si l'email existe déjà
        HTTPException(500): Si erreur lors de l'inscription
    """
    # Vérifier si l'email existe déjà
    existing_user = get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    # Hashage du mot de passe
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), salt)

    # Ajouter l'utilisateur
    success = add_user(user_data.email, user_data.username, hashed_password.decode('utf-8'))
    if not success:
        raise HTTPException(status_code=500, detail="Erreur lors de l'inscription")
    return {"message": "Inscription réussie"}

# ================================
# Route admin - Liste des utilisateurs
# ================================
@router.get("/admin/users")
def get_all_users():
    """Récupère la liste de tous les utilisateurs (sqlite3 natif)"""
    from database import get_db
    users = []
    with get_db() as conn:
        cur = conn.execute("SELECT id, email, username FROM users")
        for row in cur.fetchall():
            users.append({
                "id": row["id"],
                "email": row["email"],
                "username": row["username"]
            })
    return users

@router.delete("/admin/users/{user_id}")
def delete_user(user_id: int):
    """Supprime un utilisateur et ses commandes (sqlite3 natif)"""
    from database import get_db
    with get_db() as conn:
        # Vérifier si l'utilisateur existe
        cur = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cur.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        # Supprimer les commandes et items associés (si tables order/orderitem existent)
        try:
            conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            return {"message": "Utilisateur supprimé avec succès"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression de l'utilisateur: {e}")

# ================================
# Route de connexion
# ================================
@router.post("/login")
def login(credentials: dict):
    """Connexion d'un utilisateur (sqlite3 natif)
    
    Paramètres:
        credentials (dict): Identifiants (email, password)
    
    Retourne:
        dict: Token d'accès JWT
    
    Lève:
        HTTPException(400): Si email non trouvé ou mot de passe incorrect
    """
    db_user = get_user_by_email(credentials["email"])
    if not db_user:
        raise HTTPException(status_code=400, detail="Email non trouvé")
    if not bcrypt.checkpw(credentials["password"].encode('utf-8'), db_user["hashed_password"].encode('utf-8')):
        raise HTTPException(status_code=400, detail="Mot de passe incorrect")
    # Créer et retourner le token JWT avec user_id
    access_token = create_access_token(data={"sub": db_user["email"], "user_id": db_user["id"]})
    return {"access_token": access_token, "token_type": "bearer", "user_id": db_user["id"], "username": db_user["username"]}

@router.get("/me")
def get_current_user(token: str = Depends(oauth2_scheme)):
    """Retourne les infos de l'utilisateur courant à partir du JWT"""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Impossible de valider les identifiants",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        user_id = payload.get("user_id")
        if not email and not user_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = None
    if user_id:
        # Try to get by user_id if present
        from database import get_db
        with get_db() as conn:
            cur = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = cur.fetchone()
    if not user and email:
        user = get_user_by_email(email)
    if user is None:
        raise credentials_exception
    return {"id": user["id"], "email": user["email"], "username": user["username"]}
