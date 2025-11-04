# app/domain/interfaces/i_crud.py

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

# Interfaz Base para Servicios que Modifican Datos
class ICRUD(ABC):
    @abstractmethod
    def add(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nuevo recurso."""
        pass

    @abstractmethod
    def query(self, query_params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Consulta uno o más recursos (ej: Catálogo)."""
        pass

    @abstractmethod
    def update(self, key: Any, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza un recurso existente."""
        pass

    @abstractmethod
    def delete(self, key: Any) -> bool:
        """Elimina un recurso."""
        pass

# Interfaz ICRUDAR (Solo Lectura/Consulta - Usada por Catálogo y Dashboard)
class ICRUDAR(ICRUD):
    # Hereda query. Las clases que implementen esto deberán lanzar error o no implementar add/update/delete.
    @abstractmethod
    def add(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("ICRUDAR no implementa la creación.")
    # Repetir para update y delete...

# Interfaz ICRUDE (Añade métodos específicos - Usada por Login y Pedidos (cliente))
class ICRUDE(ICRUD):

    @abstractmethod
    def update_status(self, key: Any, new_status: str) -> Dict[str, Any]:
        """Método específico para Pedidos (Cambio de estado/anulación)."""
        pass