# app/domain/entities/order.py

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class OrderItem:
    """Una línea de producto dentro del pedido."""
    product_id: int
    product_name: str
    quantity: int
    price_unit: float # Precio final unitario pagado
    
@dataclass
class Order:
    """Entidad principal del Pedido."""
    order_id: Optional[int] = None
    user_id: int = 0
    items: List[OrderItem] = list
    
    # Datos de la transacción
    total_paid: float = 0.0
    shipping_address: str = ""
    payment_method: str = "" 
    
    # Control de estado (según tu diagrama)
    status: str = "pendiente_pago" # Estados: pendiente_pago, pagado, enviado, entregado, cancelado
    
    # Fechas
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()