# main.py
# Archivo de demostración de la arquitectura de backend COMPLETA y CORREGIDA.

from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.product_repository import ProductRepository
from app.infrastructure.repositories.cart_repository import CartRepository
from app.infrastructure.repositories.order_repository import OrderRepository

from app.application.services.register_service import RegisterService
from app.application.services.login_service import LoginService
from app.application.services.catalogue_service import CatalogueService
from app.application.services.shopping_cart import ShoppingCartService
from app.application.services.payment_service import PaymentService
from app.application.services.order_service import OrderService
from app.application.services.dashboard_service import DashboardService
from app.application.services.client_profile_service import ClientProfileService
from app.application.services.invoice_service import InvoiceService, EmailAdapter

import json

# Datos de prueba consistentes
TEST_EMAIL = "cliente_ecomarket_final@test.cl"
TEST_PASSWORD = "password_seguro_123"


def run_full_integration_test():
    """
    Simula el flujo completo de un cliente y la administración para validar toda la arquitectura.
    """
    print("\n" + "="*80)
    print("      INICIANDO TEST DE INTEGRACIÓN FINAL CON MONGO Y ECOMARKET")
    print("="*80 + "\n")

    # ----------------------------------------------------
    # FASE 1: INICIALIZACIÓN DE COMPONENTES CORE
    # ----------------------------------------------------
    print("--- 1. INICIALIZACIÓN DE REPOSITORIOS Y ADAPTERS ---")
    
    try:
        user_repo = UserRepository() 
        product_repo = ProductRepository() 
        cart_repo = CartRepository()
        order_repo = OrderRepository()
        email_adapter = EmailAdapter() 
        payment_service = PaymentService() 
    except Exception as e:
        print(f"[ERROR CRÍTICO] Falló la conexión a MongoDB. Verifica tu URI en db_connector.py. Deteniendo. Error: {e}")
        return
    
    # ----------------------------------------------------
    # FASE 2: INICIALIZACIÓN DE SERVICIOS
    # ----------------------------------------------------
    register_service = RegisterService(user_repository=user_repo)
    login_service = LoginService(user_repository=user_repo)
    profile_service = ClientProfileService(user_repository=user_repo)
    catalogue_service = CatalogueService(product_repository=product_repo)
    cart_service = ShoppingCartService(cart_repository=cart_repo, product_repository=product_repo)
    order_service = OrderService(order_repo, cart_repo, product_repo, payment_service)
    invoice_service = InvoiceService(email_adapter)
    dashboard_service = DashboardService(product_repo, order_repo, user_repo)
    
    # ----------------------------------------------------
    # FASE 3: FLUJO DEL CLIENTE (REGISTRO Y LOGIN)
    # ----------------------------------------------------
    print("\n--- 3. FLUJO DE AUTENTICACIÓN Y PERFIL ---")
    
    # 3a. Registro (Intentamos, si ya existe, no importa)
    register_result = register_service.add({"email": TEST_EMAIL, "password": TEST_PASSWORD, "nombre": "Rocío Ecomarket"})
    print(f"Resultado Registro: {register_result['status']} | Mensaje: {register_result.get('message', 'Registro Exitoso')}")
    
    # 3b. Login (Obtenemos el ID del usuario, si existe)
    login_result = login_service.login(TEST_EMAIL, TEST_PASSWORD)
    if login_result['status'] == 'error':
        print(f"[ERROR FATAL] Falló el login: {login_result['message']}. Deteniendo.")
        return
        
    user_id = login_result['user_data']['user_id']
    print(f"Resultado Login: {login_result['status']} (ID: {user_id})")

    # 3c. Consulta y Actualización de Perfil
    profile_update = profile_service.update(user_id, {'nombre': 'Rocío (Cliente Final)', 'direccion': 'Av. Las Frutas 101'})
    print(f"Resultado Update Perfil: {profile_update['status']}")


    # ----------------------------------------------------
    # FASE 4: FLUJO DE COMPRA (CATÁLOGO Y CARRITO)
    # ----------------------------------------------------
    print("\n--- 4. FLUJO DE COMPRA ---")
    
    # Consulta de Catálogo
    catalogue = catalogue_service.query()
    print(f"Productos Activos en Catálogo: {len(catalogue)}")
    
    if len(catalogue) < 2:
        print("[AVISO] No hay suficientes productos (Se requieren 2). Falló la inicialización.")
        return

    # Usamos los dos primeros productos disponibles de la lista
    product_item_1_id = catalogue[0]['product_id'] 
    product_item_2_id = catalogue[1]['product_id']

    print(f"Productos Seleccionados (Manzana/Tomate IDs): {product_item_1_id}, {product_item_2_id}")

    # Añadir al Carrito (Manzana y Tomate)
    cart_service.add({'user_id': user_id, 'product_id': product_item_1_id, 'quantity': 5}) # 5 unidades
    cart_service.add({'user_id': user_id, 'product_id': product_item_2_id, 'quantity': 2}) # 2 unidades
    
    # Consulta del Carrito (Manejo de errores del Key 'items')
    cart_view = cart_service.query({'user_id': user_id})

    if cart_view.get('status') == 'error':
        print(f"[ERROR CARRITO] Falló la consulta: {cart_view.get('message', 'Respuesta inesperada')}. Deteniendo.")
        return
    
    print(f"Carrito Actualizado: Ítems: {len(cart_view['items'])} | Total: ${cart_view['total']}")
        
    # Stock antes del checkout (Manzana Roja)
    item_1_stock_before = product_repo.get_by_id(product_item_1_id).stock
    print(f"Stock Manzana Roja antes de pagar: {item_1_stock_before}")

    # ----------------------------------------------------
    # FASE 5: CHECKOUT COMPLETO (PAGO, PEDIDO, STOCK, BOLETA)
    # ----------------------------------------------------
    print("\n--- 5. CHECKOUT Y PROCESAMIENTO TRANSACCIONAL ---")
    
    checkout_data = {
        "user_id": user_id,
        "card_data": {"card_number": "1111222233334444", "cvv": "123"}, 
        "shipping_address": "Av. Las Frutas 101"
    }

    # Proceso de Checkout (Llama a Pago, Orden, Stock, Limpia Carrito)
    checkout_result = order_service.add(checkout_data)
    order_id = checkout_result.get('order_id')
    print(f"Resultado Checkout: {checkout_result['status']} | Pedido ID: {order_id} | Total: ${checkout_result.get('total')}")
    
    if checkout_result['status'] == 'error':
        print(f"[ERROR CHECKOUT] El checkout falló. Deteniendo.")
        return

    # 5a. Reducción de Stock (Verificación)
    item_1_stock_after = product_repo.get_by_id(product_item_1_id).stock
    print(f"Stock Manzana Roja después de pagar: {item_1_stock_after} (Debería ser {item_1_stock_before - 5})")
    
    # 5b. Envío de Boleta (Notificación)
    final_order = order_repo.get_by_id(order_id)
    invoice_result = invoice_service.generate_and_send(final_order, TEST_EMAIL)
    print(f"Resultado Envío Boleta: {invoice_result['status']}")

    # ----------------------------------------------------
    # FASE 6: FLUJO ADMINISTRATIVO (ACTUALIZACIÓN Y REPORTE)
    # ----------------------------------------------------
    print("\n--- 6. FLUJO ADMINISTRATIVO Y DASHBOARD ---")
    
    # 6a. Actualización de Estado de Pedido 
    status_update = order_service.update_status(order_id, "entregado")
    print(f"Resultado Update Estado: {status_update['status']} -> {status_update.get('new_status')}")

    # 6b. Consulta del Dashboard (Reporte)
    dashboard_report = dashboard_service.query()
    
    print("\n--- REPORTE FINAL DEL DASHBOARD ---")
    print(f"Ingreso Total (por el pedido actual): ${dashboard_report['metrics']['total_revenue']:.2f}")
    print(f"Órdenes Procesadas: {dashboard_report['metrics']['total_orders_processed']}")
    print(f"Distribución de Órdenes: {dashboard_report['orders_breakdown']}")
    
    print("\n" + "="*80)
    print("                 ¡TEST DE INTEGRACIÓN COMPLETADO CON ÉXITO!")
    print("================================================================================\n")


if __name__ == "__main__":
    run_full_integration_test()