# =================================
# Script de gestion de la BDD
# =================================

from database import init_db
from sqlmodel import Session, create_engine

# Configuration de la base de données
DATABASE_URL = "sqlite:///database.db"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# ================================
# Point d'entrée du script
# ================================

if __name__ == "__main__":
    # Initialisation de la base de données
    print("Initialisation de la base de données...")
    init_db()
    print("Base de données initialisée avec succès !")
    input("\nAppuyez sur Entrée pour quitter...")
    try:
        pass
    except Exception as e:
        print(f"Erreur: {e}")
