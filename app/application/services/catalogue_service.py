# app/application/services/catalogue_service.py

from app.domain.interfaces.i_crud import ICRUDAR
from app.infrastructure.repositories.product_repository import ProductRepository
from typing import Dict, Any, List, Optional
import json

class CatalogueService(ICRUDAR):
    """
    Clase que implementa la lógica de consulta pública del catálogo de productos (ICRUDAR).
    Sólo muestra productos activos y con stock.
    """
    def __init__(self, product_repository: ProductRepository):
        # Inyección de dependencia
        self.product_repo = product_repository


    # IMPLEMENTACIÓN ESENCIAL: Método 'query' (Lectura Pública)
    

    def query(self, query_params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        [READ] Obtiene la lista de productos visibles al público.
        """
        all_products = self.product_repo.get_all()
        
        # Lógica de Negocio: Filtrar por estado 'activo' y stock > 0
        visible_products = [
            p.__dict__ for p in all_products 
            if p.estado == 'activo' and p.stock > 0
        ]
        
        # Aquí se aplicaría lógica de filtros por categoría o búsqueda si vinieran en query_params.
        
        return visible_products


    # MÉTODOS NO IMPLEMENTADOS (Contrato ICRUDAR)
    
    def add(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("CatalogueService es solo de lectura.")
    
    def update(self, key: Any, input_data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("CatalogueService es solo de lectura.")

    def delete(self, key: Any) -> bool:
        raise NotImplementedError("CatalogueService es solo de lectura.")