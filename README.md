# GameStore

GameStore is a full-stack web project for browsing and ordering video games across multiple platforms. It combines a static frontend with a FastAPI backend and a local SQLite database, making it easy to run and demonstrate locally.

## Overview

The project includes:

- A storefront for PC, PlayStation 5, and Xbox games
- User registration and login with JWT authentication
- Shopping cart and checkout flow
- Order history and order management
- Contact form handling
- Admin features for managing users, orders, messages, and products

## Tech Stack

- Frontend: HTML, CSS, JavaScript
- Backend: FastAPI
- Database: SQLite
- Authentication: JWT + bcrypt
- Local development servers: `uvicorn` and Python `http.server`

## Project Structure

```text
.
|-- backend/
|   |-- main.py
|   |-- database.py
|   |-- auth.py
|   |-- routes/
|   `-- requirements.txt
|-- FRONTend/
|   |-- index.html
|   |-- style.css
|   |-- script.js
|   `-- images/
|-- start.py
`-- README.md
```

## Features

### Customer Features

- Browse the catalog by platform
- Register and sign in
- Add products to favorites and cart
- Place orders with shipping details
- View personal order history

### Admin Features

- Manage orders and update their status
- Review and delete contact messages
- Manage users
- Create, update, hide, and delete products
- Upload product images

## Getting Started

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd techno22-update-fonctionne
```

### 2. Install dependencies

```bash
pip install -r backend/requirements.txt
```

### 3. Run the application

```bash
python start.py
```

This command starts:

- The backend API at `http://127.0.0.1:8000`
- The frontend at `http://127.0.0.1:8090/index.html`
- The API documentation at `http://127.0.0.1:8000/docs`

## API Modules

The backend is organized into the following route groups:

- `auth_routes.py` for registration, login, user profile, and admin user management
- `order_routes.py` for order creation, listing, deletion, and status updates
- `contact_routes.py` for contact form submissions and message management
- `product_routes.py` for product catalog access, admin product management, and image upload

## Database

The application uses a local SQLite database stored in:

```text
backend/gamestore.db
```

On startup, the backend automatically:

- Creates missing tables
- Seeds the product catalog if the database is empty

## Development Notes

- This project is intended for local development, demos, or academic use
- CORS is open to all origins for easier local testing
- Uploaded product images are stored in `FRONTend/images/uploads/`

## License

This repository does not currently include a license file. Add one before publishing if you want to define reuse permissions clearly.
