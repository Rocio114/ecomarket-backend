# app/infrastructure/repositories/cart_repository.py

from app.domain.interfaces.i_repository import IRepository
from app.domain.entities.cart import Cart
from app.infrastructure.db_connector import MongoDBConnector
from typing import List, Optional, Any
from bson.objectid import ObjectId
import json

class CartRepository(IRepository[Cart]):

    def __init__(self):
        # Conexión a la colección "carts"
        self.collection = MongoDBConnector.get_collection("carts")
    
    # En un sistema real, el Cart ID es el User ID, o se usa un ID de sesión.
    # Aquí buscamos el carrito por el user_id.
    def get_by_user_id(self, user_id: str) -> Optional[Cart]:
        """ Recupera un carrito usando el user_id (clave primaria lógica). """
        cart_data = self.collection.find_one({"user_id": user_id})
        if cart_data:
            cart_data['cart_id'] = str(cart_data.pop('_id'))
            return Cart.from_dict(cart_data) # Usamos el método de la entidad para recrear el objeto
        return None

    def get_by_id(self, item_id: Any) -> Optional[Cart]:
        # En este contexto, el item_id es el _id de MongoDB
        cart_data = self.collection.find_one({"_id": ObjectId(item_id)})
        if cart_data:
            cart_data['cart_id'] = str(cart_data.pop('_id'))
            return Cart.from_dict(cart_data)
        return None
        
    def get_all(self) -> List[Cart]:
        carts_list = []
        for cart_data in self.collection.find():
            cart_data['cart_id'] = str(cart_data.pop('_id'))
            carts_list.append(Cart.from_dict(cart_data))
        return carts_list

    def save(self, entity: Cart) -> Cart:
        # Usamos to_dict para asegurar que los Item_Carts anidados sean serializados
        cart_data = entity.to_dict() 
        
        if entity.cart_id is None:
            # Si es la primera vez que se guarda (creación del carrito)
            result = self.collection.insert_one(cart_data)
            entity.cart_id = str(result.inserted_id)
        else:
            # Si el carrito ya existe (actualización de ítems)
            cart_id_mongo = ObjectId(entity.cart_id)
            cart_data.pop('cart_id') # Eliminar para evitar que se guarde como un campo
            
            self.collection.update_one(
                {"_id": cart_id_mongo},
                {"$set": cart_data}
            )
            # Devolvemos la entidad con su ID
            entity.cart_id = str(cart_id_mongo) 
            
        return entity

    def delete(self, item_id: Any) -> bool:
        result = self.collection.delete_one({"_id": ObjectId(item_id)})
        return result.deleted_count > 0