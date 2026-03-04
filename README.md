# GameStore

GameStore est une application web e-commerce de jeux video (PC, Xbox, PlayStation 5) developpee en **full-stack** avec un frontend HTML/CSS/JavaScript et un backend FastAPI (Python) connecte a SQLite.

## Demo en ligne : https://badreddinemadad05.github.io/Gamestore/index.html

## Fonctionnalites principales

### Cote utilisateur
- Inscription et connexion
- Consultation du catalogue par plateforme
- Ajout de jeux au panier
- Gestion des favoris
- Paiement et creation de commande
- Consultation du profil et de l'historique de commandes

### Cote administrateur
- Tableau de bord admin
- Gestion des commandes (lecture, statut, suppression)
- Gestion des utilisateurs
- Gestion des messages de contact
- Gestion des produits (ajout, modification, suppression, upload image)

## Technologies utilisees

- **Frontend** : HTML, CSS, JavaScript
- **Backend** : Python, FastAPI, Uvicorn
- **Base de donnees** : SQLite
- **Authentification** : JWT + bcrypt

## Tester le site

1. Ouvrir la demo :  
   https://badreddinemadad05.github.io/Gamestore/index.html
2. Creer un compte (Sign In)
3. Se connecter
4. Ajouter des jeux au panier et aux favoris
5. Passer une commande depuis la page de paiement
6. Verifier le profil / historique des commandes

## Structure du projet

- `FRONTend/` : pages HTML, style CSS, scripts JS
- `backend/` : API FastAPI, routes, logique base de donnees
- `start.py` : lancement local du frontend + backend

## Auteur

Projet realise par **Badreddine Madad**.
