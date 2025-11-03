# app/infrastructure/repositories/user_repository.py

from app.domain.interfaces.i_repository import IRepository
from app.domain.entities.user import User
from typing import List, Optional, Any, Dict

class UserRepository(IRepository[User]):
    """
    Implementación del IRepository para la entidad User.
    Simula la conexión a DB_PostgreSQL usando una lista en memoria (in-memory list).
    """
    
    # SIMULACIÓN DE BASE DE DATOS (En memoria)
    # En la realidad, esto sería una conexión ORM (SQLAlchemy/Django ORM)
    
    _users: List[User] = []
    _next_id: int = 1


    # IMPLEMENTACIÓN DE CONTRATOS DE IRepository

    def get_by_id(self, item_id: Any) -> Optional[User]:
        """Obtiene un usuario por user_id."""
        for user in self._users:
            if user.user_id == item_id:
                return user
        return None

    def get_all(self) -> List[User]:
        """Obtiene todos los usuarios (admin dashboard)."""
        # Retorna una copia para evitar modificación externa de la lista interna
        return self._users.copy()

    def save(self, entity: User) -> User:
        """Guarda o actualiza un usuario."""
        
        # Simulación de un INSERT (si no tiene ID)
        if entity.user_id is None:
            entity.user_id = self._next_id
            self._next_id += 1
            self._users.append(entity)
            return entity
        
        # Simulación de un UPDATE (si ya tiene ID)
        for i, user in enumerate(self._users):
            if user.user_id == entity.user_id:
                self._users[i] = entity
                return entity
        
        # Si el ID existe pero no está en la lista (caso borde de simulación)
        self._users.append(entity)
        return entity

    def delete(self, item_id: Any) -> bool:
        """Elimina un usuario por user_id."""
        original_count = len(self._users)
        self._users[:] = [user for user in self._users if user.user_id != item_id]
        return len(self._users) < original_count
        
    # MÉTODOS DE BÚSQUEDA ESPECÍFICA (Añadido para Login/Registro)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Método de repositorio específico para el login."""
        for user in self._users:
            if user.email == email:
                return user
        return None