# app/application/services/register_service.py

from app.domain.interfaces.i_crud import ICRUD
from app.domain.interfaces.i_repository import IRepository
from app.domain.entities.user import User
from typing import Any, Dict, List, Optional

# Simulamos la dependencia del Repositorio de Usuarios
# Nota: La inyección de dependencia es clave en esta arquitectura
class RegisterService(ICRUD):
    """
    Clase que implementa la lógica de registro de nuevos usuarios (Historia B-02).
    Hereda de ICRUD para el método 'add'.
    """
    def __init__(self, user_repository: IRepository[User]):
        # El servicio depende de una implementación de IRepository (Inyección)
        self.user_repository = user_repository

    # ----------------------------------------------------
    # IMPLEMENTACIÓN ESENCIAL: Método 'add' (Registrar Usuario)
    # ----------------------------------------------------
    def add(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Registra un nuevo usuario Cliente.
        """
        # 1. Validar la entrada (ej: que el email no exista, que la contraseña sea segura)
        # Esto sería lógica de validación real. Por ahora, asumimos éxito.

        # 2. Simular Hashing de Contraseña (Requerimiento de Seguridad)
        # NOTA: En la realidad, usarías bcrypt aquí.
        fake_hash = f"hashed_{input_data['password']}_secure"
        
        # 3. Crear la Entidad Pura (Dominio)
        new_user = User(
            email=input_data['email'],
            password_hash=fake_hash,
            nombre=input_data.get('nombre', 'Nuevo Cliente'),
            rol='client'
        )

        # 4. Usar el Repositorio (Persistencia) para guardar la entidad
        saved_user = self.user_repository.save(new_user)
        
        # 5. Retornar la respuesta (sin el hash de la contraseña)
        return {
            "status": "success",
            "user_id": saved_user.user_id,
            "email": saved_user.email,
            "rol": saved_user.rol
        }
        
    # MÉTODOS NO IMPLEMENTADOS (Fuera de Alcance de Registro)
    
    def query(self, query_params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        # La clase Registro no se encarga de consultar listados, por lo que lanzamos la excepción
        raise NotImplementedError("RegistroService solo implementa 'add'.")

    def update(self, key: Any, input_data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("RegistroService no implementa actualización.")

    def delete(self, key: Any) -> bool:
        raise NotImplementedError("RegistroService no implementa eliminación.")