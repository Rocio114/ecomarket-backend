# app/application/services/invoice_service.py

from app.domain.entities.order import Order
from typing import Dict, Any

class EmailAdapter:
    """
    Simulación del Módulo de Infraestructura que se comunica con el Servidor_Email 
    (Interfaz: Servicio_Notif).
    """
    def send_email(self, recipient: str, subject: str, body: str) -> bool:
        """
        Simula la llamada al Motor_SMTP del Servidor_Email.
        """
        print(f"\n[INFRA - EMAIL] Enviando correo a: {recipient}")
        print(f"[INFRA - EMAIL] Asunto: {subject}")
        # En un sistema real, aquí se usaría la librería SMTP o una API como SendGrid.
        return True # Asumimos éxito en la entrega

class InvoiceService:
    """
    Clase que implementa la lógica de generación y envío de la Boleta (Facturación).
    Utiliza el EmailAdapter para la comunicación externa.
    """
    def __init__(self, email_adapter: EmailAdapter):
        # Inyección de dependencia del adaptador de infraestructura
        self.email_adapter = email_adapter

    def generate_and_send(self, order: Order, recipient_email: str) -> Dict[str, Any]:
        """
        Genera el contenido de la boleta y notifica al cliente por email.
        """
        print(f"\n[SERVICIO BOLETA] Generando boleta para Pedido ID: {order.order_id}")
        
        # 1. Generación de Contenido (Simulación del Módulo de Plantillas)
        # Esto simula el formato de la boleta
        invoice_body = self._format_invoice_content(order)
        
        subject = f"Confirmación de Compra y Boleta #{order.order_id} - Ecomarket"
        
        # 2. Llamada al Adaptador (Servidor_Email)
        success = self.email_adapter.send_email(recipient_email, subject, invoice_body)
        
        if success:
            return {"status": "success", "message": "Boleta generada y enviada correctamente por email."}
        else:
            return {"status": "error", "message": "Error al enviar el email de la boleta."}

    def _format_invoice_content(self, order: Order) -> str:
        """
        Helper: Genera un texto simple para la simulación de la boleta.
        """
        items_list = "\n".join([
            f"- {item.product_name} x{item.quantity} (${item.price_unit})" 
            for item in order.items
        ])
        
        return (
            f"--- BOLETA ELECTRÓNICA ECOMARKET ---\n"
            f"PEDIDO ID: {order.order_id}\n"
            f"FECHA: {order.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"DIRECCIÓN DE ENVÍO: {order.shipping_address}\n"
            f"------------------------------------\n"
            f"PRODUCTOS:\n{items_list}\n"
            f"------------------------------------\n"
            f"TOTAL PAGADO: ${order.total_paid}\n"
            f"ESTADO: {order.status.upper()}\n"
            f"¡Gracias por su compra!"
        )