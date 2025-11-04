# app/infrastructure/repositories/product_repository.py

from app.domain.interfaces.i_repository import IRepository
from app.domain.entities.product import Product
from typing import List, Optional, Any

class ProductRepository(IRepository[Product]):
    """
    Implementación del IRepository para la entidad Product.
    Simula la conexión a DB_PostgreSQL usando una lista en memoria.
    Esta es la capa de Persistencia.
    """
    
    # SIMULACIÓN DE BASE DE DATOS (En memoria)
    
    _products: List[Product] = []
    _next_id: int = 1

    def __init__(self):
        # Inicializa con algunos datos de prueba
        if not self._products:
            self._products.extend([
                self.save(Product(nombre="Laptop Gamer", descripcion="PC para juegos", precio_float=1200.0, stock=5, categoria="Electrónica")),
                self.save(Product(nombre="Teclado Mecánico", descripcion="Razer Chroma", precio_float=150.0, stock=20, categoria="Accesorios")),
                self.save(Product(nombre="Monitor 4K", descripcion="Pantalla curva", precio_float=500.0, stock=10, categoria="Electrónica")),
            ])
            
            
    # IMPLEMENTACIÓN DE CONTRATOS DE IRepository
    

    def get_by_id(self, item_id: Any) -> Optional[Product]:
        """Obtiene un producto por product_id."""
        for product in self._products:
            if product.product_id == item_id:
                return product
        return None

    def get_all(self) -> List[Product]:
        """Obtiene todos los productos."""
        # Se podría filtrar por estado='activo' aquí si fuera necesario
        return [p for p in self._products if p.estado == 'activo']

    def save(self, entity: Product) -> Product:
        """Guarda o actualiza un producto."""
        
        # Simulación de un INSERT (si no tiene ID)
        if entity.product_id is None:
            entity.product_id = self._next_id
            self._next_id += 1
            self._products.append(entity)
            return entity
        
        # Simulación de un UPDATE (si ya tiene ID)
        for i, product in enumerate(self._products):
            if product.product_id == entity.product_id:
                self._products[i] = entity
                return entity
        
        # Si no se encontró el ID, se agrega como nuevo
        self._products.append(entity)
        return entity

    def delete(self, item_id: Any) -> bool:
        """Elimina un producto por product_id."""
        original_count = len(self._products)
        self._products[:] = [p for p in self._products if p.product_id != item_id]
        return len(self._products) < original_count