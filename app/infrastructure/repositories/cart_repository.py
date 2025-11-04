# app/infrastructure/repositories/cart_repository.py

from app.domain.interfaces.i_repository import IRepository
from app.domain.entities.cart import Cart, CartItem
from typing import List, Optional, Any, Dict

class CartRepository(IRepository[Cart]):
    """
    Implementación del IRepository para la entidad Cart.
    Simula la conexión a DB_PostgreSQL usando un diccionario en memoria, 
    donde la clave es el cart_id.
    """
    
    # SIMULACIÓN DE BASE DE DATOS (En memoria)
    # _carts_by_id: {1: Cart(1, 101, [...]), 2: Cart(2, 102, [...])}
    
    _carts_by_id: Dict[int, Cart] = {}
    _next_id: int = 1
    
    # También simulamos una búsqueda por user_id, ya que el carrito es único por usuario
    _carts_by_user_id: Dict[int, Cart] = {} 


    # IMPLEMENTACIÓN DE CONTRATOS DE IRepository
    

    def get_by_id(self, item_id: Any) -> Optional[Cart]:
        """Obtiene un carrito por cart_id."""
        return self._carts_by_id.get(item_id)

    def get_all(self) -> List[Cart]:
        """Obtiene todos los carritos (principalmente para fines administrativos o debugging)."""
        return list(self._carts_by_id.values())

    def save(self, entity: Cart) -> Cart:
        """Guarda o actualiza un carrito."""
        
        # Simulación de un INSERT (si no tiene ID)
        if entity.cart_id is None:
            entity.cart_id = self._next_id
            self._next_id += 1
        
        # Simulación de un UPDATE/INSERT
        self._carts_by_id[entity.cart_id] = entity
        self._carts_by_user_id[entity.user_id] = entity # Mantiene el mapa de usuario a carrito
        return entity

    def delete(self, item_id: Any) -> bool:
        """Elimina un carrito por cart_id."""
        cart_to_delete = self._carts_by_id.pop(item_id, None)
        if cart_to_delete:
            self._carts_by_user_id.pop(cart_to_delete.user_id, None)
            return True
        return False
    
    
    # MÉTODO ESPECÍFICO DE LÓGICA DE NEGOCIO
    
    def get_by_user_id(self, user_id: int) -> Optional[Cart]:
        """Obtiene el carrito único de un usuario."""
        return self._carts_by_user_id.get(user_id)