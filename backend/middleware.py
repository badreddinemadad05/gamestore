# =================================
# Middleware de logging
# =================================

from fastapi import Request
import logging
from jose import JWTError, jwt

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Clé secrète et algorithme pour le JWT
SECRET_KEY = "dev_secret"  # À synchroniser avec la clé utilisée pour signer les tokens
ALGORITHM = "HS256"

# ================================
# Middleware de journalisation
# ================================

async def log_middleware(request: Request, call_next):
    """Middleware pour journaliser les requêtes HTTP
    
    Paramètres:
        request (Request): Requête HTTP entrante
        call_next (callable): Fonction pour continuer le traitement
    
    Retourne:
        Response: Réponse HTTP
        
    Note:
        Enregistre la méthode et l'URL de chaque requête
        avant son traitement
    """
    # Log de la requête entrante
    logger.info(f"Request: {request.method} {request.url}")
    
    # Traitement de la requête
    response = await call_next(request)
    
    return response

# =================================
# Middleware d'extraction de l'ID utilisateur
# =================================

async def user_id_middleware(request: Request, call_next):
    """Middleware pour extraire l'ID utilisateur du token JWT (Authorization: Bearer ...)"""
    auth_header = request.headers.get("Authorization")
    user_id = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("user_id")
            if user_id is not None:
                user_id = int(user_id)
        except (JWTError, ValueError):
            user_id = None
    request.state.user_id = user_id
    
    # Traitement de la requête
    response = await call_next(request)
    
    return response