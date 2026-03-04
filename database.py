# =================================
# Configuration de la base de données (sqlite3 natif)
# =================================
import sqlite3
from contextlib import contextmanager
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gamestore.db")

# ================================
# Fonctions de gestion de la BDD
# ================================
@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Crée toutes les tables si elles n'existent pas déjà"""
    with get_db() as conn:
        # Table des utilisateurs
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                username TEXT NOT NULL,
                hashed_password TEXT NOT NULL
            )
        ''')
        
        # Table des commandes
        conn.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                total_amount REAL NOT NULL,
                shipping_address TEXT NOT NULL,
                shipping_city TEXT NOT NULL,
                shipping_postal_code TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                special_instructions TEXT,
                order_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Table des articles de commande
        conn.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_name TEXT NOT NULL,
                product_price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                product_image TEXT,
                FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE
            )
        ''')
        
        # Table des messages de contact
        conn.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                subject TEXT,
                message TEXT NOT NULL,
                date_sent TEXT DEFAULT CURRENT_TIMESTAMP,
                is_read INTEGER DEFAULT 0
            )
        ''')

        # Table des produits
        conn.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                platform TEXT NOT NULL,
                genre TEXT NOT NULL,
                price REAL NOT NULL,
                stock INTEGER NOT NULL DEFAULT 0,
                visible INTEGER NOT NULL DEFAULT 1,
                image TEXT NOT NULL,
                badge TEXT,
                description TEXT
            )
        ''')

        # Seed initial des produits si la table est vide
        count_row = conn.execute("SELECT COUNT(*) AS count FROM products").fetchone()
        if count_row and count_row["count"] == 0:
            seed_products = [
                ("Minecraft", "pc", "Simulation", 14.99, 25, 1, "images/pc_sim_1.png", "bestseller", "Jeu bac a sable creatif"),
                ("ZOO PLANET", "pc", "Simulation", 64.99, 8, 1, "images/pc_sim_2.png", "hot", "Gestion et construction de zoo"),
                ("Call Of Duty : WARZONE", "pc", "Action / Aventure", 29.99, 15, 1, "images/pc_act_2.png", "discount", "FPS multijoueur"),
                ("Football Manager 2025", "pc", "Sport", 24.49, 12, 1, "images/pc_sp_1.png", "discount", "Gestion d equipe de football"),
                ("Rocket League", "pc", "Sport", 22.99, 20, 1, "images/pc_sp_2.png", "bestseller", "Football arcade en voiture"),
                ("FORTNITE", "pc", "Action / Aventure", 34.49, 30, 1, "images/pc_act_1.png", None, "Battle royale"),
                ("Clair Obscur: Expedition 33", "pc", "Action / Aventure", 29.99, 6, 1, "images/pc_act_3.png", "new", "RPG narratif"),
                ("ARK : Survival Ascended", "xbox", "Action / Aventure", 34.99, 10, 1, "images/xbox_act_1.png", "new", "Survie en monde ouvert"),
                ("MADDEN NFL 25 Xbox", "xbox", "Sport", 39.99, 14, 1, "images/xbox_sp_3.png", "hot", "Simulation de football americain"),
                ("Grand Theft Auto V", "xbox", "Simulation", 22.49, 16, 1, "images/xbox_sim_4.png", "bestseller", "Action sandbox"),
                ("FORZZA MOTORSPORT", "xbox", "Sport", 59.99, 9, 1, "images/xbox_sp_1.png", "new", "Course automobile"),
                ("EA SPORTS FC 24 Xbox", "xbox", "Sport", 69.99, 7, 1, "images/xbox_sp_2.png", None, "Football"),
                ("ASTRONEER", "xbox", "Action / Aventure", 24.99, 11, 1, "images/xbox_act_2.png", "new", "Exploration spatiale"),
                ("Atomfall", "xbox", "Action / Aventure", 29.99, 13, 1, "images/xbox_act_3.png", None, "Action aventure"),
                ("ALIENS : DARK DESCENT", "xbox", "Action / Aventure", 19.99, 9, 1, "images/xbox_act_4.png", None, "Strategie tactique"),
                ("Farming Simulator 22", "xbox", "Simulation", 14.99, 17, 1, "images/xbox_sim_1.png", None, "Simulation agricole"),
                ("Disney Dreamlight Valley", "xbox", "Simulation", 44.99, 10, 1, "images/xbox_sim_2.png", "new", "Simulation de vie"),
                ("Call of the Wild : The Angler", "xbox", "Simulation", 27.49, 8, 1, "images/xbox_sim_3.png", "new", "Simulation de peche"),
                ("Death Stranding", "ps5", "Action / Aventure", 59.99, 12, 1, "images/ps5_act_1.png", "new", "Aventure cinematographique"),
                ("God Of War", "ps5", "Action / Aventure", 24.99, 22, 1, "images/ps5_act_3.png", "bestseller", "Action mythologique"),
                ("The Last of Us", "ps5", "Action / Aventure", 39.99, 18, 1, "images/ps5_act_2.png", "bestseller", "Action aventure"),
                ("EA Sports 25", "ps5", "Sport", 54.99, 11, 1, "images/ps5_sp_1.png", "discount", "Football"),
                ("Street Fighter 6", "ps5", "Sport", 39.99, 14, 1, "images/ps5_sp_2.png", "hot", "Combat"),
                ("WWE 2K25", "ps5", "Sport", 49.99, 10, 1, "images/ps5_sp_3.png", None, "Catch"),
            ]
            conn.executemany(
                """
                INSERT INTO products (name, platform, genre, price, stock, visible, image, badge, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                seed_products,
            )
        
        conn.commit()

# Fonction pour ajouter un utilisateur
def add_user(email, username, hashed_password):
    with get_db() as conn:
        try:
            conn.execute(
                "INSERT INTO users (email, username, hashed_password) VALUES (?, ?, ?)",
                (email, username, hashed_password)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Email déjà utilisé

# Fonction pour rechercher un utilisateur par email
def get_user_by_email(email):
    with get_db() as conn:
        cur = conn.execute("SELECT * FROM users WHERE email = ?", (email,))
        return cur.fetchone()
