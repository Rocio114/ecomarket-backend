# app/domain/interfaces/i_repository.py

from abc import ABC, abstractmethod
from typing import TypeVar, List, Generic, Any, Optional

T = TypeVar('T')  # Representa la entidad (Usuario, Producto, Pedido)

class IRepository(ABC, Generic[T]):
    @abstractmethod
    def get_by_id(self, item_id: Any) -> Optional[T]:
        """Obtiene una entidad por su ID."""
        pass

    @abstractmethod
    def get_all(self) -> List[T]:
        """Obtiene todas las entidades."""
        pass

    @abstractmethod
    def save(self, entity: T) -> T:
        """Guarda o actualiza una entidad."""
        pass

    @abstractmethod
    def delete(self, item_id: Any) -> bool:
        """Elimina una entidad por su ID."""
        pass