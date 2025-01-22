from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor


app = FastAPI(
    title="Products API",
    description="API para gestión de productos",
    version="1.0.0"
)


# Configuración de la base de datos
DB_CONFIG = {
    "host": "localhost",
    "database": "ecommerce",
    "user": "postgres",
    "password": "1234",
}

@contextmanager
def get_db_connection():
    """Context manager para manejar la conexión a la base de datos"""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
        yield conn
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error de conexión a la base de datos: {str(e)}"
        )
    finally:
        if conn is not None:
            conn.close()

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)

class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True

@app.post("/products", response_model=ProductResponse, status_code=201)
async def create_product(product: ProductBase):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO products (name, description, price)
                VALUES (%s, %s, %s)
                RETURNING id, name, description, price;
                """,
                (product.name, product.description, product.price)
            )
            conn.commit()
            return cursor.fetchone()
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=f"Error al crear el producto: {str(e)}")

@app.get("/products", response_model=List[ProductResponse])
async def get_products():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM products ORDER BY id;")
            products = cursor.fetchall()
            return products or []
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al obtener productos: {str(e)}")

@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM products WHERE id = %s;", (product_id,))
            product = cursor.fetchone()
            if not product:
                raise HTTPException(status_code=404, detail="Producto no encontrado")
            return product
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al obtener el producto: {str(e)}")

@app.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, product: ProductBase):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE products
                SET name = %s, description = %s, price = %s
                WHERE id = %s
                RETURNING id, name, description, price;
                """,
                (product.name, product.description, product.price, product_id)
            )
            conn.commit()
            updated_product = cursor.fetchone()
            if not updated_product:
                raise HTTPException(status_code=404, detail="Producto no encontrado")
            return updated_product
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=f"Error al actualizar el producto: {str(e)}")

@app.delete("/products/{product_id}", status_code=204)
async def delete_product(product_id: int):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM products WHERE id = %s RETURNING id;", (product_id,))
            conn.commit()
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Producto no encontrado")
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=f"Error al eliminar el producto: {str(e)}")

@app.get("/")
async def root():
    return {
        "message": "Bienvenido a la API de Productos",
        "docs": "/docs",
        "redoc": "/redoc"
    }