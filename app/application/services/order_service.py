# app/application/services/order_service.py

from app.domain.interfaces.i_crud import ICRUD, ICRUDE
from app.infrastructure.repositories.order_repository import OrderRepository
from app.infrastructure.repositories.cart_repository import CartRepository
from app.infrastructure.repositories.product_repository import ProductRepository
from app.application.services.payment_service import PaymentService # Dependencia del servicio de pago
from app.domain.entities.order import Order, OrderItem
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

class OrderService(ICRUDE):
    """
    Clase que implementa la lógica de gestión de pedidos (Clientes y Admin).
    Orquesta los repositorios y servicios externos (Pago).
    """
    def __init__(self, 
                 order_repo: OrderRepository, 
                 cart_repo: CartRepository, 
                 product_repo: ProductRepository, 
                 payment_service: PaymentService):
        # Inyección de todas las dependencias necesarias
        self.order_repo = order_repo
        self.cart_repo = cart_repo
        self.product_repo = product_repo
        self.payment_service = payment_service


    # IMPLEMENTACIÓN ESENCIAL: Método 'add' (Checkout)


    def add(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        [CREATE] Procesa el checkout: (1) Valida, (2) Paga, (3) Crea Pedido, (4) Limpia Carrito y Stock.
        """
        user_id = input_data['user_id']
        card_data = input_data['card_data']
        shipping_address = input_data['shipping_address']

        # 1. Obtener y Validar Carrito
        cart = self.cart_repo.get_by_user_id(user_id)
        if not cart or not cart.items:
            return {"status": "error", "message": "El carrito está vacío."}
        
        # Recalcular el total final
        from app.application.services.shopping_cart import ShoppingCartService
        cart_service = ShoppingCartService(self.cart_repo, self.product_repo)
        total_price = cart_service._calculate_total(cart)
        
        # 2. Llamar al Servicio de Pago (Pasarela Externa)
        payment_result = self.payment_service.process_payment(total_price, card_data)
        
        if not payment_result['success']:
            return {"status": "error", "message": f"Pago rechazado: {payment_result['message']}"}

        # --- TRANSACCIÓN EXITOSA: CREAR PEDIDO Y ACTUALIZAR STOCK ---
        
        # 3. Crear la Entidad Pedido (Order)
        order_items = [
            OrderItem(
                product_id=item.product_id,
                product_name=self.product_repo.get_by_id(item.product_id).nombre, # Nombre del catálogo
                quantity=item.quantity,
                price_unit=item.price_unit
            ) for item in cart.items
        ]
        
        new_order = Order(
            user_id=user_id,
            items=order_items,
            total_paid=total_price,
            shipping_address=shipping_address,
            payment_method="Tarjeta (Simulado)",
            status="pagado" # Estado inicial después del pago exitoso
        )
        
        saved_order = self.order_repo.save(new_order)
        
        # 4. Actualizar Stock y Limpiar Carrito
        for item in cart.items:
            product = self.product_repo.get_by_id(item.product_id)
            if product:
                product.stock -= item.quantity # Reducir Stock
                self.product_repo.save(product)
        
        self.cart_repo.delete(cart.cart_id) # Limpiar Carrito
        
        return {"status": "success", "order_id": saved_order.order_id, "total": saved_order.total_paid, "message": "Pedido procesado y pago confirmado."}


    # IMPLEMENTACIÓN DE CONTRATOS ADICIONALES
    

    def query(self, query_params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        [READ] Consulta pedidos (Clientes: propios / Admin: todos).
        """
        user_id = query_params.get('user_id')
        
        if user_id:
            # Clientes solo ven sus pedidos
            orders = self.order_repo.get_by_user_id(user_id)
        else:
            # Admin o sin filtro ve todos los pedidos
            orders = self.order_repo.get_all()
        
        # Convertir entidades Order a diccionarios
        return [o.__dict__ for o in orders]

    def update(self, key: Any, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        [UPDATE] Actualiza información del pedido (Admin).
        """
        # Lógica para Admin: cambiar dirección, agregar tracking, etc. (Omitido por brevedad)
        raise NotImplementedError("La actualización general de pedidos está reservada para el Admin.")
        
    def delete(self, key: Any) -> bool:
        """
        [DELETE] Solo eliminación física (Admin).
        """
        return self.order_repo.delete(key)

    def update_status(self, key: Any, new_status: str) -> Dict[str, Any]:
        """
        [ICRUDE] Actualiza el estado del pedido (ej: 'enviado', 'cancelado').
        """
        order = self.order_repo.get_by_id(key)
        if not order:
            return {"status": "error", "message": "Pedido no encontrado."}

        VALID_STATUS = ["pagado", "enviado", "entregado", "cancelado"]

        if new_status not in VALID_STATUS:
            return {"status": "error", "message": f"Estado '{new_status}' no válido."}

        order.status = new_status
        self.order_repo.save(order)
        
        return {"status": "success", "order_id": order.order_id, "new_status": new_status, "message": "Estado del pedido actualizado."}