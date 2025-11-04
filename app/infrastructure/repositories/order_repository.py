# app/infrastructure/repositories/order_repository.py

from app.domain.interfaces.i_repository import IRepository
from app.domain.entities.order import Order
from app.infrastructure.db_connector import MongoDBConnector
from typing import List, Optional, Any, Dict
from datetime import datetime # ¡Verificado!
from bson.objectid import ObjectId

class OrderRepository(IRepository[Order]):

    def __init__(self):
        # Conexión a la colección "orders"
        self.collection = MongoDBConnector.get_collection("orders")

    def get_by_id(self, item_id: Any) -> Optional[Order]:
        # El ID de la orden será el _id de MongoDB
        order_data = self.collection.find_one({"_id": ObjectId(item_id)})
        if order_data:
            order_data['order_id'] = str(order_data.pop('_id'))
            return Order.from_dict(order_data)
        return None

    def get_all(self) -> List[Order]:
        orders_list = []
        for order_data in self.collection.find():
            order_data['order_id'] = str(order_data.pop('_id'))
            orders_list.append(Order.from_dict(order_data))
        return orders_list

    def save(self, entity: Order) -> Order:
        # Usamos to_dict para serializar la entidad completa (incluyendo ítems anidados)
        order_data = entity.to_dict()
        
        if entity.order_id is None:
            # INSERT: Insertamos una nueva orden
            result = self.collection.insert_one(order_data)
            entity.order_id = str(result.inserted_id)
        else:
            # UPDATE: Actualizamos una orden existente (ej. cambio de estado)
            order_id_mongo = ObjectId(entity.order_id)
            order_data.pop('order_id')
            
            # Aseguramos que el campo 'updated_at' siempre se actualice en el documento
            order_data['updated_at'] = datetime.now()
            
            self.collection.update_one(
                {"_id": order_id_mongo},
                {"$set": order_data}
            )
            entity.order_id = str(order_id_mongo)
            
        return entity

    def delete(self, item_id: Any) -> bool:
        result = self.collection.delete_one({"_id": ObjectId(item_id)})
        return result.deleted_count > 0

    def update_status(self, order_id: Any, new_status: str) -> Optional[Order]:
        # Este método específico solo actualiza el estado y el timestamp
        order_id_mongo = ObjectId(order_id)
        
        self.collection.update_one(
            {"_id": order_id_mongo},
            {"$set": {
                "status": new_status, 
                "updated_at": datetime.now()
            }}
        )
        # Recuperamos y retornamos la orden actualizada
        return self.get_by_id(order_id)