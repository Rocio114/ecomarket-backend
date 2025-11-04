# app/domain/entities/cart.py

from dataclasses import dataclass
from typing import Optional, List, Dict, Any

@dataclass
class CartItem:
    """Una línea de producto dentro del carrito."""
    product_id: int
    quantity: int
    price_unit: float # Precio al momento de añadir (para evitar cambios en el catálogo)

@dataclass
class Cart:
    """Entidad principal del Carrito."""
    cart_id: Optional[int] = None
    user_id: int = 0
    items: List[CartItem] = list
    total_price: float = 0.0 # Este valor se calcula en el servicio, no se persiste directamente