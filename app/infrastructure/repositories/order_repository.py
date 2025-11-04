# app/infrastructure/repositories/order_repository.py

from app.domain.interfaces.i_repository import IRepository
from app.domain.entities.order import Order
from typing import List, Optional, Any, Dict

class OrderRepository(IRepository[Order]):
    """
    Implementación del IRepository para la entidad Order (Pedido).
    Simula la conexión a DB_PostgreSQL usando un diccionario en memoria.
    Esta es la capa de Persistencia.
    """
    
    # SIMULACIÓN DE BASE DE DATOS (En memoria)
    
    _orders_by_id: Dict[int, Order] = {}
    _next_id: int = 1


    # IMPLEMENTACIÓN DE CONTRATOS DE IRepository
    

    def get_by_id(self, item_id: Any) -> Optional[Order]:
        """Obtiene un pedido por order_id."""
        return self._orders_by_id.get(item_id)

    def get_all(self) -> List[Order]:
        """Obtiene todos los pedidos (principalmente para el Admin)."""
        return list(self._orders_by_id.values())

    def save(self, entity: Order) -> Order:
        """Guarda o actualiza un pedido."""
        
        # Simulación de un INSERT (si no tiene ID)
        if entity.order_id is None:
            entity.order_id = self._next_id
            self._next_id += 1
        
        # Simulación de un UPDATE/INSERT
        entity.updated_at = datetime.now()
        self._orders_by_id[entity.order_id] = entity
        return entity

    def delete(self, item_id: Any) -> bool:
        """Elimina un pedido por order_id."""
        return self._orders_by_id.pop(item_id, None) is not None
    
    
    # MÉTODOS ESPECÍFICOS DE LÓGICA DE NEGOCIO
    
    def get_by_user_id(self, user_id: int) -> List[Order]:
        """Obtiene todos los pedidos de un usuario específico (para el cliente)."""
        return [order for order in self._orders_by_id.values() if order.user_id == user_id]