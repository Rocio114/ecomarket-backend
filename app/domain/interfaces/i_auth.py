# app/domain/interfaces/i_auth.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class IAuth(ABC):
    """Contrato específico para servicios de autenticación (Login)."""
    @abstractmethod
    def login(self, email: str, password: str) -> Dict[str, Any]: pass