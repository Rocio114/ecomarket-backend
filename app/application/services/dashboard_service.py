# app/application/services/dashboard_service.py

from app.domain.interfaces.i_crud import ICRUDAR
from app.infrastructure.repositories.product_repository import ProductRepository
from app.infrastructure.repositories.order_repository import OrderRepository
from app.infrastructure.repositories.user_repository import UserRepository
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

class DashboardService(ICRUDAR):
    """
    Clase que implementa la lógica de análisis y métricas para el Dashboard del Admin.
    Interactúa con múltiples repositorios (Analysis/Reporting).
    """
    def __init__(self, product_repo: ProductRepository, order_repo: OrderRepository, user_repo: UserRepository):
        # Inyección de dependencias de todos los repositorios necesarios
        self.product_repo = product_repo
        self.order_repo = order_repo
        self.user_repo = user_repo


    # IMPLEMENTACIÓN ESENCIAL: Método 'query' (Reportes Admin)
    

    def query(self, query_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        [READ] Genera las métricas clave para el administrador.
        """
        
        # Obtener datos de todos los repositorios
        all_orders = self.order_repo.get_all()
        all_products = self.product_repo.get_all()
        all_users = self.user_repo.get_all()

        # Lógica de Métricas Clave (Simulación)
        
        # 1. Ventas e Ingresos
        total_revenue = sum(order.total_paid for order in all_orders if order.status in ['pagado', 'enviado', 'entregado'])
        
        # 2. Productos y Stock
        total_stock = sum(p.stock for p in all_products)
        products_out_of_stock = len([p for p in all_products if p.stock == 0])
        
        # 3. Usuarios
        total_users = len(all_users)
        
        # 4. Análisis de Pedidos (por estado)
        orders_by_status = {}
        for order in all_orders:
            orders_by_status[order.status] = orders_by_status.get(order.status, 0) + 1

        return {
            "status": "success",
            "report_date": datetime.now().isoformat(),
            "metrics": {
                "total_revenue": total_revenue,
                "total_orders_processed": len(all_orders),
                "total_users": total_users,
                "total_products_stock": total_stock,
                "products_out_of_stock": products_out_of_stock
            },
            "orders_breakdown": orders_by_status
        }


    # MÉTODOS NO IMPLEMENTADOS (Contrato ICRUDAR)
    

    def add(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("DashboardService es solo de lectura.")
    
    def update(self, key: Any, input_data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("DashboardService es solo de lectura.")

    def delete(self, key: Any) -> bool:
        raise NotImplementedError("DashboardService es solo de lectura.")