# app/application/services/login_service.py

from app.domain.interfaces.i_auth import IAuth
from app.infrastructure.repositories.user_repository import UserRepository # Importamos la implementación
from typing import Dict, Any, List, Optional

# Nota: En un sistema real, usarías una librería de hashing como 'bcrypt'
# y un servicio de tokens como 'PyJWT' aquí.

class LoginService(IAuth):
    """
    Clase que implementa la lógica de inicio de sesión de usuarios (Historia B-14).
    Implementa el método 'login' del contrato ICRUDE.
    """
    def __init__(self, user_repository: UserRepository):
        # Inyección de dependencia: El servicio NECESITA una instancia del Repositorio.
        self.user_repository = user_repository


    # IMPLEMENTACIÓN ESENCIAL: Método 'login' (Autenticación)
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Verifica las credenciales y autentica al usuario.
        """
        # 1. Buscar usuario por email usando el Repositorio
        user = self.user_repository.get_by_email(email)

        # 2. Verificar existencia y contraseña
        if not user:
            return {"status": "error", "message": "Credenciales inválidas (usuario no encontrado)"}

        # Simulación de verificación de hash: Comparamos la contraseña recibida con el hash
        # NOTA: En la vida real: hash_lib.check_password(password, user.password_hash)
        expected_hash = f"hashed_{password}_secure"
        
        if user.password_hash == expected_hash:
            # 3. Éxito: Generar Token de Sesión (Simulado)
            token = f"TOKEN_GENERADO_PARA_{user.user_id}_ROL_{user.rol}"
            
            return {
                "status": "success",
                "user_id": user.user_id,
                "email": user.email,
                "rol": user.rol,
                "token": token
            }
        else:
            return {"status": "error", "message": "Credenciales inválidas (contraseña incorrecta)"}
