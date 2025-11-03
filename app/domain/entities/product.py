# app/domain/entities/product.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class Product:
    product_id: Optional[int] = None
    nombre: str = ""
    descripcion: str = ""
    precio_float: float = 0.0
    stock: int = 0
    categoria: str = ""
    imagen_url: Optional[str] = None
    
    # Enum de tu diagrama (activo, inactivo, agotado)
    estado: str = "activo"