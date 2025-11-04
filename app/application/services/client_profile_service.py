# app/application/services/client_profile_service.py

from app.domain.interfaces.i_crud import ICRUD
from app.infrastructure.repositories.user_repository import UserRepository
from typing import Dict, Any, List, Optional
import json

class ClientProfileService(ICRUD):
    """
    Clase que implementa la lógica ICRUD para la gestión del Perfil del Cliente 
    (consulta y actualización de datos personales, Historia B-15).
    """
    def __init__(self, user_repository: UserRepository):
        # Inyección de dependencia
        self.user_repo = user_repository


    # IMPLEMENTACIÓN ESENCIAL: Método 'query' (getperfil)
    

    def query(self, query_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        [READ] Obtiene la información del perfil del cliente (getperfil).
        """
        user_id = query_params.get('user_id')
        
        if not user_id:
            return {"status": "error", "message": "Se requiere 'user_id' para obtener el perfil."}

        user = self.user_repo.get_by_id(user_id)
        
        if not user:
            return {"status": "error", "message": "Usuario no encontrado."}
        
        # Convertir la entidad a diccionario y eliminar datos sensibles
        user_data = user.__dict__.copy()
        user_data.pop('password_hash', None) 

        return {"status": "success", "profile": user_data}


    # IMPLEMENTACIÓN ESENCIAL: Método 'update' (Actualización de Perfil)
    

    def update(self, key: Any, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        [UPDATE] Actualiza los datos personales del cliente.
        key: user_id
        """
        user_id = key
        
        # 1. Obtener la entidad actual
        user = self.user_repo.get_by_id(user_id)
        
        if not user:
            return {"status": "error", "message": f"Usuario con ID {user_id} no encontrado."}
            
        # 2. Aplicar solo los cambios permitidos (Lógica de Negocio)
        user.nombre = input_data.get('nombre', user.nombre)
        user.direccion = input_data.get('direccion', user.direccion)
        user.telefono = input_data.get('telefono', user.telefono)
        # NOTA: El email y el rol NO deberían actualizarse en este servicio por seguridad.
        
        # 3. Usar el Repositorio para guardar (actualizar)
        updated_user = self.user_repo.save(user)
        
        # Retornar datos actualizados (sin hash)
        return {"status": "success", "user_id": updated_user.user_id, "message": "Perfil actualizado correctamente"}


    # MÉTODOS NO IMPLEMENTADOS 
    

    def add(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("La creación de usuarios debe usar RegisterService.")

    def delete(self, key: Any) -> bool:
        raise NotImplementedError("El cliente no puede eliminarse a sí mismo.")