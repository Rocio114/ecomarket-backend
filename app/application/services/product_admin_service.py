# app/application/services/product_admin_service.py

from app.domain.interfaces.i_crud import ICRUD
from app.infrastructure.repositories.product_repository import ProductRepository
from app.domain.entities.product import Product
from typing import Dict, Any, List, Optional
import json

class ProductAdminService(ICRUD):
    """
    Clase que implementa la lógica ICRUD para la gestión de productos por el Administrador 
    (Historias B-16 y B-17).
    """
    def __init__(self, product_repository: ProductRepository):
        # Inyección de dependencia: el servicio recibe el repositorio
        self.product_repository = product_repository


    # IMPLEMENTACIÓN DEL CONTRATO ICRUD
    

    def add(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        [CREATE] Crea un nuevo producto en el catálogo.
        """
        # Validación de stock/precio (Lógica de Negocio)
        if input_data.get('precio_float', 0) <= 0 or input_data.get('stock', 0) <= 0:
            return {"status": "error", "message": "El precio y stock deben ser positivos."}
            
        # 1. Crear la Entidad Pura (Dominio)
        new_product = Product(
            nombre=input_data['nombre'],
            descripcion=input_data.get('descripcion', ''),
            precio_float=input_data['precio_float'],
            stock=input_data['stock'],
            categoria=input_data.get('categoria', 'General')
        )
        
        # 2. Usar el Repositorio para guardar
        saved_product = self.product_repository.save(new_product)
        
        return {"status": "success", "product_id": saved_product.product_id, "nombre": saved_product.nombre}

    def query(self, query_params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        [READ] Consulta todos los productos (incluyendo inactivos, para el Admin).
        """
        # El administrador consulta todos los productos, no solo los 'activos'
        products = self.product_repository.get_all() 
        
        # Convertir las entidades Product (dataclasses) a diccionarios para la salida de la API
        return [p.__dict__ for p in products]

    def update(self, key: Any, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        [UPDATE] Actualiza un producto existente (ej: stock, precio, estado).
        """
        # 1. Obtener la entidad actual
        existing_product = self.product_repository.get_by_id(key)
        
        if not existing_product:
            return {"status": "error", "message": f"Producto con ID {key} no encontrado."}
            
        # 2. Aplicar cambios a la entidad
        existing_product.nombre = input_data.get('nombre', existing_product.nombre)
        existing_product.precio_float = input_data.get('precio_float', existing_product.precio_float)
        existing_product.stock = input_data.get('stock', existing_product.stock)
        existing_product.estado = input_data.get('estado', existing_product.estado) # Actualización de estado
        
        # 3. Usar el Repositorio para guardar (actualizar)
        updated_product = self.product_repository.save(existing_product)
        
        return {"status": "success", "product_id": updated_product.product_id, "message": "Producto actualizado correctamente"}

    def delete(self, key: Any) -> bool:
        """
        [DELETE] Elimina un producto.
        """
        # Lógica de Negocio: Podríamos hacer una 'eliminación lógica' (estado='inactivo')
        # En esta implementación, haremos una eliminación física (del repositorio simulado)
        return self.product_repository.delete(key)