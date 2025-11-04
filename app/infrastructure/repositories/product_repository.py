# app/infrastructure/repositories/product_repository.py (VERSIÓN MONGO DB FINAL CORREGIDA)

from app.domain.interfaces.i_repository import IRepository
from app.domain.entities.product import Product
from app.infrastructure.db_connector import MongoDBConnector
from typing import List, Optional, Any
from bson.objectid import ObjectId

class ProductRepository(IRepository[Product]):

    def __init__(self):
        # Conexión a la colección "products"
        self.collection = MongoDBConnector.get_collection("products")
        # Aseguramos que haya datos iniciales de prueba (con nombres de campos correctos)
        self._initialize_data()

    def _initialize_data(self):
        """ Inicializa datos de prueba si la colección está vacía. """
        
        # Opcional: LIMPIEZA TEMPORAL para asegurar que no queden campos 'precio' viejos
        # Puedes eliminar esta línea después de la primera ejecución exitosa
        # self.collection.delete_many({}) 
        
        if self.collection.count_documents({}) == 0:
            print("[INFRA - MONGO] Inicializando datos de productos con nombres de campos correctos...")
            products_data = [
                # ¡CORREGIDO! Usando 'precio_float'
                {"nombre": "Laptop Gamer X", "descripcion": "Potente para juegos y trabajo.", "precio_float": 1200.00, "stock": 5, "estado": "activo", "categoria": "Electrónica"}, 
                {"nombre": "Teclado Mecánico RGB", "descripcion": "Switches rápidos y duraderos.", "precio_float": 85.50, "stock": 20, "estado": "activo", "categoria": "Accesorios"},
                {"nombre": "Monitor Curvo 27''", "descripcion": "144Hz, ideal para diseño.", "precio_float": 350.00, "stock": 10, "estado": "activo", "categoria": "Electrónica"},
            ]
            self.collection.insert_many(products_data)

    def get_by_id(self, item_id: Any) -> Optional[Product]:
        """Obtiene un producto por product_id, manejando la conversión de ID."""
        
        # CORRECCIÓN DE ID: Aseguramos que el ID sea una cadena para usar ObjectId
        # La lógica de la aplicación puede pasar un int o un string ObjectId.
        if not isinstance(item_id, str):
            item_id = str(item_id)
            
        try:
            product_data = self.collection.find_one({"_id": ObjectId(item_id)})
        except Exception:
            # Si el string no es un ObjectId válido (ej. "1", "2"), simplemente no se encuentra.
            return None 

        if product_data:
            # Convertir el _id de MongoDB (ObjectId) al product_id de la entidad (str)
            product_data['product_id'] = str(product_data.pop('_id'))
            return Product(**product_data)
        return None

    def get_all(self) -> List[Product]:
        """Obtiene todos los productos de la colección."""
        products_list = []
        for product_data in self.collection.find():
            product_data['product_id'] = str(product_data.pop('_id'))
            products_list.append(Product(**product_data))
        return products_list

    def save(self, entity: Product) -> Product:
        """Guarda o actualiza una entidad de producto."""
        product_data = entity.__dict__.copy()

        if entity.product_id is None:
            # INSERT: Insertamos el diccionario sin ID
            result = self.collection.insert_one(product_data)
            entity.product_id = str(result.inserted_id)
        else:
            # UPDATE: Usamos el ID de la entidad para encontrar y actualizar
            product_id_mongo = ObjectId(entity.product_id)
            product_data.pop('product_id') # Eliminamos el campo para el $set
            
            self.collection.update_one(
                {"_id": product_id_mongo},
                {"$set": product_data}
            )
            # Reasignamos el ID a la entidad después del update
            entity.product_id = str(product_id_mongo) 
            
        return entity

    def delete(self, item_id: Any) -> bool:
        """Elimina un producto por su ID (ObjectId)."""
        result = self.collection.delete_one({"_id": ObjectId(item_id)})
        return result.deleted_count > 0