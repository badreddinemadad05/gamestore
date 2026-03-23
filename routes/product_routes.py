import os
import uuid

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from pydantic import BaseModel, Field
from typing import Optional
from database import get_db

router = APIRouter()

UPLOAD_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "FRONTend", "images", "uploads")
)
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


class ProductCreate(BaseModel):
    name: str = Field(min_length=1)
    platform: str = Field(min_length=1)
    genre: str = Field(min_length=1)
    price: float = Field(ge=0)
    stock: int = Field(ge=0)
    visible: bool = True
    image: str = Field(min_length=1)
    badge: Optional[str] = None
    description: Optional[str] = None


class ProductUpdate(BaseModel):
    name: str = Field(min_length=1)
    platform: str = Field(min_length=1)
    genre: str = Field(min_length=1)
    price: float = Field(ge=0)
    stock: int = Field(ge=0)
    visible: bool
    image: str = Field(min_length=1)
    badge: Optional[str] = None
    description: Optional[str] = None


@router.get("/products")
def get_products(
    platform: Optional[str] = None,
    include_hidden: bool = Query(default=False),
):
    query = "SELECT * FROM products WHERE 1=1"
    params = []

    if platform:
        query += " AND LOWER(platform) = LOWER(?)"
        params.append(platform)

    if not include_hidden:
        query += " AND visible = 1"

    query += " ORDER BY name ASC"

    with get_db() as conn:
        rows = conn.execute(query, tuple(params)).fetchall()
        return [
            {
                "id": row["id"],
                "name": row["name"],
                "platform": row["platform"],
                "genre": row["genre"],
                "price": row["price"],
                "stock": row["stock"],
                "visible": bool(row["visible"]),
                "image": row["image"],
                "badge": row["badge"],
                "description": row["description"],
            }
            for row in rows
        ]


@router.get("/admin/products")
def admin_get_products(platform: Optional[str] = None):
    query = "SELECT * FROM products WHERE 1=1"
    params = []

    if platform:
        query += " AND LOWER(platform) = LOWER(?)"
        params.append(platform)

    query += " ORDER BY id DESC"

    with get_db() as conn:
        rows = conn.execute(query, tuple(params)).fetchall()
        return [
            {
                "id": row["id"],
                "name": row["name"],
                "platform": row["platform"],
                "genre": row["genre"],
                "price": row["price"],
                "stock": row["stock"],
                "visible": bool(row["visible"]),
                "image": row["image"],
                "badge": row["badge"],
                "description": row["description"],
            }
            for row in rows
        ]


@router.post("/admin/products")
def admin_create_product(payload: ProductCreate):
    with get_db() as conn:
        cur = conn.execute(
            """
            INSERT INTO products (name, platform, genre, price, stock, visible, image, badge, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.name,
                payload.platform.lower(),
                payload.genre,
                payload.price,
                payload.stock,
                1 if payload.visible else 0,
                payload.image,
                payload.badge,
                payload.description,
            ),
        )
        conn.commit()
        return {"message": "Produit cree", "id": cur.lastrowid}


@router.put("/admin/products/{product_id}")
def admin_update_product(product_id: int, payload: ProductUpdate):
    with get_db() as conn:
        existing = conn.execute("SELECT id FROM products WHERE id = ?", (product_id,)).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Produit non trouve")

        conn.execute(
            """
            UPDATE products
            SET name = ?, platform = ?, genre = ?, price = ?, stock = ?, visible = ?, image = ?, badge = ?, description = ?
            WHERE id = ?
            """,
            (
                payload.name,
                payload.platform.lower(),
                payload.genre,
                payload.price,
                payload.stock,
                1 if payload.visible else 0,
                payload.image,
                payload.badge,
                payload.description,
                product_id,
            ),
        )
        conn.commit()
        return {"message": "Produit mis a jour"}


@router.delete("/admin/products/{product_id}")
def admin_delete_product(product_id: int):
    with get_db() as conn:
        existing = conn.execute("SELECT id FROM products WHERE id = ?", (product_id,)).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Produit non trouve")
        conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        return {"message": "Produit supprime"}


@router.post("/admin/upload-image")
async def admin_upload_image(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Fichier invalide")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Format image non supporte")

    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Le fichier doit etre une image")

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    safe_name = f"{uuid.uuid4().hex}{ext}"
    abs_path = os.path.join(UPLOAD_DIR, safe_name)

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Fichier vide")

    if len(content) > 6 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image trop lourde (max 6 MB)")

    with open(abs_path, "wb") as out:
        out.write(content)

    return {
        "message": "Image uploadee",
        "path": f"images/uploads/{safe_name}",
    }

