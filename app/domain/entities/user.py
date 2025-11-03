# app/domain/entities/user.py

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime

@dataclass
class User:
    user_id: Optional[int] = None
    email: str = ""
    password_hash: str = "" 
    rol: str = "client" # 'client' o 'admin'
    
    # Atributos de perfil (ajustar según tu diagrama)
    nombre: str = ""
    direccion: str = ""
    telefono: Optional[str] = None
    fecha_nacimiento: Optional[datetime] = None