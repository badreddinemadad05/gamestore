### backend/main.py

# =================================
# Main - Point d'entrée de l'API
# =================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routes import auth_routes, order_routes, contact_routes, product_routes
from middleware import log_middleware, user_id_middleware

# Création de l'application FastAPI
app = FastAPI(
    title="GameStore API",
    description="API pour la gestion du magasin de jeux vidéo",
    version="1.0.0"
)

# ================================
# Configuration CORS
# ================================
"""Configuration du middleware CORS pour permettre les requêtes cross-origin

Paramètres:
    allow_origins: Liste des origines autorisées ("*" pour toutes)
    allow_credentials: Autoriser l'envoi des cookies
    allow_methods: Méthodes HTTP autorisées
    allow_headers: Headers HTTP autorisés
"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les domaines exacts
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware custom
app.middleware("http")(log_middleware)
app.middleware("http")(user_id_middleware)

# ================================
# Enregistrement des routes
# ================================
"""Inclusion des différents modules de routes

Routes:
    /api/users: Authentification et gestion des utilisateurs
    /api: Gestion des commandes
    /api: Gestion des messages de contact
"""
app.include_router(
    auth_routes.router,
    prefix="/api/users",
    tags=["users"]
)

app.include_router(
    order_routes.router,
    prefix="/api",
    tags=["orders"]
)

app.include_router(
    contact_routes.router,
    prefix="/api",
    tags=["contact"]
)

app.include_router(
    product_routes.router,
    prefix="/api",
    tags=["products"]
)

@app.on_event("startup")
def startup():
    init_db()
