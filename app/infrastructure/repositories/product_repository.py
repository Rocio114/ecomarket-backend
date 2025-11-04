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
        
        # Opcional: LIMPIEZA TEMPORAL si aún no la has borrado
        # self.collection.delete_many({}) 
        
        if self.collection.count_documents({}) == 0:
            print("[INFRA - MONGO] Inicializando datos de ECOMARKET (Frutas y Verduras)...")
            products_data = [
                # Producto 1 (Frutas)
                {"nombre": "Manzana Roja", "descripcion": "Manzanas frescas, perfectas para comer.", "precio_float": 1.50, "stock": 50, "estado": "activo", "categoria": "Frutas"}, 
                # Producto 2 (Verduras)
                {"nombre": "Tomate Larga Vida", "descripcion": "Tomates maduros para ensaladas.", "precio_float": 0.75, "stock": 120, "estado": "activo", "categoria": "Verduras"},
                # Producto 3 (Frutas)
                {"nombre": "Plátano Orgánico", "descripcion": "Plátanos de Ecuador, altos en potasio.", "precio_float": 0.90, "stock": 80, "estado": "activo", "categoria": "Frutas"},
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