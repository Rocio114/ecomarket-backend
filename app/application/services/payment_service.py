# app/application/services/payment_service.py

from typing import Dict, Any

class PaymentService:
    """
    Clase que simula la comunicación con la Pasarela de Pago Externa (Servicio_Pago).
    Esta simulación representa el 'Adapter' o 'Contrato' de la API externa.
    """
    def __init__(self):
        # En un sistema real, aquí se inicializarían las credenciales 
        # para la API de la pasarela de pago (ej., Stripe, Transbank, PayPal).
        print("[INFRA] PaymentService inicializado, listo para simular pagos.")

    def process_payment(self, total_amount: float, card_data: Dict[str, str]) -> Dict[str, Any]:
        """
        Simula el procesamiento de un pago con la pasarela externa.

        Args:
            total_amount: Monto total del pedido.
            card_data: Diccionario con datos simulados de la tarjeta (número, vencimiento, etc.).

        Returns:
            Un diccionario con el resultado de la transacción.
        """
        print(f"[INFRA] Intentando procesar pago de ${total_amount}...")

        # Lógica de Simulación: Falla si el número de tarjeta termina en '000'
        if card_data.get('card_number', '').endswith('000'):
            return {
                "success": False,
                "transaction_id": None,
                "message": "Pago Rechazado. Fondos insuficientes (Error de simulación)."
            }
        
        # Simulación de Éxito:
        transaction_id = f"TRX-{hash(total_amount)}-{len(card_data.get('card_number', ''))}"
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "message": "Pago Aprobado y Recibido."
        }