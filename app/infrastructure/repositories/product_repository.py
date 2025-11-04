# app/infrastructure/repositories/product_repository.py

from app.domain.interfaces.i_repository import IRepository
from app.domain.entities.product import Product
from app.infrastructure.db_connector import MongoDBConnector
from typing import List, Optional, Any
from bson.objectid import ObjectId

class ProductRepository(IRepository[Product]):

    def __init__(self):
        # Conexión a la colección "products"
        self.collection = MongoDBConnector.get_collection("products")
        # Aseguramos que haya datos iniciales para la prueba de integración
        self._initialize_data()

    def _initialize_data(self):
        """ Inicializa datos de prueba si la colección está vacía. """
        if self.collection.count_documents({}) == 0:
            print("[INFRA - MONGO] Inicializando datos de productos...")
            products_data = [
                {"nombre": "Laptop Gamer X", "descripcion": "Potente para juegos y trabajo.", "precio": 1200.00, "stock": 5, "estado": "activo"},
                {"nombre": "Teclado Mecánico RGB", "descripcion": "Switches rápidos y duraderos.", "precio": 85.50, "stock": 0, "estado": "activo"},
                {"nombre": "Monitor Curvo 27''", "descripcion": "144Hz, ideal para diseño.", "precio": 350.00, "stock": 10, "estado": "activo"},
            ]
            self.collection.insert_many(products_data)

    def get_by_id(self, item_id: Any) -> Optional[Product]:
        product_data = self.collection.find_one({"_id": ObjectId(item_id)})
        if product_data:
            product_data['product_id'] = str(product_data.pop('_id'))
            return Product(**product_data)
        return None

    def get_all(self) -> List[Product]:
        products_list = []
        for product_data in self.collection.find():
            product_data['product_id'] = str(product_data.pop('_id'))
            products_list.append(Product(**product_data))
        return products_list

    def save(self, entity: Product) -> Product:
        product_data = entity.__dict__

        if entity.product_id is None:
            # INSERT
            result = self.collection.insert_one(product_data)
            entity.product_id = str(result.inserted_id)
        else:
            # UPDATE
            product_id_mongo = ObjectId(entity.product_id)
            product_data.pop('product_id')
            self.collection.update_one(
                {"_id": product_id_mongo},
                {"$set": product_data}
            )
            # Volvemos a asignar el ID a la entidad para ser consistente
            entity.product_id = str(product_id_mongo) 
            
        return entity

    def delete(self, item_id: Any) -> bool:
        result = self.collection.delete_one({"_id": ObjectId(item_id)})
        return result.deleted_count > 0