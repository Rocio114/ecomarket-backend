# app/infrastructure/repositories/user_repository.py

from app.domain.interfaces.i_repository import IRepository
from app.domain.entities.user import User
from app.infrastructure.db_connector import MongoDBConnector  # <-- Nueva dependencia
from typing import List, Optional, Any, Dict
from bson.objectid import ObjectId # Para manejar los IDs de MongoDB

class UserRepository(IRepository[User]):
    
    def __init__(self):
        # 1. Conexión a la colección "users"
        self.collection = MongoDBConnector.get_collection("users")
        
    def get_by_id(self, item_id: Any) -> Optional[User]:
        # MongoDB usa _id como ID principal. Convertimos el ID a ObjectId.
        user_data = self.collection.find_one({"_id": ObjectId(item_id)})
        if user_data:
            # Convertir el _id de MongoDB al user_id de la entidad
            user_data['user_id'] = str(user_data.pop('_id'))
            return User(**user_data)
        return None

    def get_all(self) -> List[User]:
        users_list = []
        for user_data in self.collection.find():
            user_data['user_id'] = str(user_data.pop('_id'))
            users_list.append(User(**user_data))
        return users_list

    def save(self, entity: User) -> User:
        user_data = entity.__dict__
        
        if entity.user_id is None:
            # INSERT: Insertamos el diccionario sin el ID
            result = self.collection.insert_one(user_data)
            user_data['user_id'] = str(result.inserted_id)
            entity.user_id = str(result.inserted_id)
        else:
            # UPDATE: Usamos el ID de la entidad para encontrar y actualizar
            user_id_mongo = ObjectId(entity.user_id)
            # Removemos el ID del diccionario para el $set
            user_data.pop('user_id') 
            self.collection.update_one(
                {"_id": user_id_mongo},
                {"$set": user_data}
            )
            user_data['_id'] = user_id_mongo # Volvemos a poner el ID para retornar
            
        return entity

    def delete(self, item_id: Any) -> bool:
        result = self.collection.delete_one({"_id": ObjectId(item_id)})
        return result.deleted_count > 0
    
    def get_by_email(self, email: str) -> Optional[User]:
        user_data = self.collection.find_one({"email": email})
        if user_data:
            user_data['user_id'] = str(user_data.pop('_id'))
            return User(**user_data)
        return None