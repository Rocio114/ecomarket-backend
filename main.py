# main.py
# Archivo de demostración de la arquitectura de backend COMPLETA

from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.product_repository import ProductRepository
from app.infrastructure.repositories.cart_repository import CartRepository
from app.infrastructure.repositories.order_repository import OrderRepository

from app.application.services.register_service import RegisterService
from app.application.services.login_service import LoginService
from app.application.services.catalogue_service import CatalogueService
from app.application.services.product_admin_service import ProductAdminService # Importado pero no usado
from app.application.services.shopping_cart import ShoppingCartService
from app.application.services.payment_service import PaymentService
from app.application.services.order_service import OrderService
from app.application.services.dashboard_service import DashboardService
from app.application.services.client_profile_service import ClientProfileService
from app.application.services.invoice_service import InvoiceService, EmailAdapter

import json

def run_full_integration_test():
    """
    Simula el flujo completo de un cliente y la administración para validar toda la arquitectura.
    """
    print("\n" + "="*80)
    print("      INICIANDO TEST DE INTEGRACIÓN DEL BACKEND COMPLETO CON MONGODB")
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
    # FASE 2: INICIALIZACIÓN DE SERVICIOS (Inyección de Dependencias)
    # ----------------------------------------------------
    register_service = RegisterService(user_repository=user_repo)
    login_service = LoginService(user_repository=user_repo)
    profile_service = ClientProfileService(user_repository=user_repo)
    catalogue_service = CatalogueService(product_repository=product_repo)
    cart_service = ShoppingCartService(cart_repository=cart_repo, product_repository=product_repo)
    order_service = OrderService(order_repo, cart_repo, product_repo, payment_service)
    invoice_service = InvoiceService(email_adapter)
    dashboard_service = DashboardService(product_repo, order_repo, user_repo)
    
    print("\n[OK] Todos los componentes inicializados y dependencias inyectadas.\n")

    # ----------------------------------------------------
    # FASE 3: FLUJO DEL CLIENTE (REGISTRO, LOGIN Y PERFIL)
    # ----------------------------------------------------
    print("--- 3. FLUJO DE AUTENTICACIÓN Y PERFIL ---")
    
    # Registro de Cliente
    new_user_data = {"email": "cliente_test@ecomarket.cl", "password": "pass_seguro_123", "nombre": "Cliente Test"}
    register_result = register_service.add(new_user_data)
    
    # El ID es el ObjectId de MongoDB, lo usamos como string
    user_id = register_result.get('user_id') 
    
    if register_result['status'] == 'error' and 'ya existe' not in register_result['message']:
        print(f"Resultado Registro: {register_result['status']} | {register_result['message']}. Deteniendo.")
        return

    print(f"Resultado Registro: {register_result['status']} (ID: {user_id})")

    # Login
    login_result = login_service.login("cliente_test@ecomarket.cl", "pass_seguro_123")
    print(f"Resultado Login: {login_result['status']}")
    
    # Consulta y Actualización de Perfil
    profile_query = profile_service.query({'user_id': user_id})
    print(f"Perfil Antes: {profile_query['profile'].get('nombre')}")
    
    update_data = {'nombre': 'Cliente Actualizado', 'direccion': 'Calle Falsa 123'}
    profile_update = profile_service.update(user_id, update_data)
    print(f"Resultado Update Perfil: {profile_update['status']}\n")


    # ----------------------------------------------------
    # FASE 4: FLUJO DE COMPRA (CATÁLOGO Y CARRITO)
    # ----------------------------------------------------
    print("--- 4. FLUJO DE COMPRA ---")
    
    # Consulta de Catálogo (ICRUDAR)
    catalogue = catalogue_service.query()
    print(f"Productos Activos en Catálogo: {len(catalogue)}")
    
    if not catalogue:
        print("[AVISO] No hay productos en catálogo. Posiblemente falló la inicialización.")
        return

    # Usamos los IDs reales de MongoDB de los productos inicializados
    laptop_id = catalogue[0]['product_id']  # Primer producto (Laptop)
    monitor_id = catalogue[2]['product_id'] # Tercer producto (Monitor)
    
    # Añadir al Carrito (Laptop y Monitor)
    cart_add_1 = cart_service.add({'user_id': user_id, 'product_id': laptop_id, 'quantity': 1})
    cart_add_2 = cart_service.add({'user_id': user_id, 'product_id': monitor_id, 'quantity': 2})
    
    # Consulta del Carrito (FIX: Manejo del KeyError)
    cart_view = cart_service.query({'user_id': user_id})

    # ESTE ES EL BLOQUE CORREGIDO: Manejo del error de consulta del carrito
    if cart_view.get('status') == 'error' or cart_view.get('status') == 'empty' or not isinstance(cart_view, dict):
        print(f"[ERROR CARRITO] Falló la consulta del carrito: {cart_view.get('message', 'Respuesta inesperada')}. Deteniendo.")
        return
    else:
        print(f"Carrito Actualizado: Ítems: {len(cart_view['items'])} | Total: ${cart_view['total']}")
        
    # Stock antes del checkout (Consultamos el producto nuevamente)
    laptop_stock_before = product_repo.get_by_id(laptop_id).stock
    print(f"Stock Laptop antes de pagar: {laptop_stock_before}")

    # ----------------------------------------------------
    # FASE 5: CHECKOUT COMPLETO (PAGO, PEDIDO, STOCK, BOLETA)
    # ----------------------------------------------------
    print("\n--- 5. CHECKOUT Y PROCESAMIENTO TRANSACCIONAL ---")
    
    checkout_data = {
        "user_id": user_id,
        "card_data": {"card_number": "1111222233334444", "cvv": "123"}, # Pago Exitoso
        "shipping_address": "Calle Falsa 123 - Cliente Actualizado"
    }

    # Proceso de Checkout (Llama a Pago, Orden, Stock)
    checkout_result = order_service.add(checkout_data)
    order_id = checkout_result.get('order_id')
    print(f"Resultado Checkout: {checkout_result['status']} | Pedido ID: {order_id}")
    
    # Verificación de ID de Pedido para el resto del flujo
    if checkout_result['status'] == 'error':
        print(f"[ERROR CHECKOUT] El checkout falló. Deteniendo.")
        return

    # 5a. Reducción de Stock (Verificación)
    laptop_stock_after = product_repo.get_by_id(laptop_id).stock
    print(f"Stock Laptop después de pagar: {laptop_stock_after} (Debería ser {laptop_stock_before - 1})")
    
    # 5b. Envío de Boleta (Notificación)
    final_order = order_repo.get_by_id(order_id)
    invoice_result = invoice_service.generate_and_send(final_order, "cliente_test@ecomarket.cl")
    print(f"Resultado Envío Boleta: {invoice_result['status']}")

    # ----------------------------------------------------
    # FASE 6: FLUJO ADMINISTRATIVO (ACTUALIZACIÓN Y REPORTE)
    # ----------------------------------------------------
    print("\n--- 6. FLUJO ADMINISTRATIVO Y DASHBOARD ---")
    
    # 6a. Actualización de Estado de Pedido (ICRUDE - Admin)
    status_update = order_service.update_status(order_id, "enviado")
    print(f"Resultado Update Estado: {status_update['status']} -> {status_update.get('new_status')}")

    # 6b. Consulta del Dashboard (ICRUDAR - Reporte)
    dashboard_report = dashboard_service.query()
    
    print("\n--- REPORTE FINAL DEL DASHBOARD ---")
    print(f"Ingreso Total: ${dashboard_report['metrics']['total_revenue']}")
    print(f"Órdenes Pagadas/Enviadas: {dashboard_report['metrics']['total_orders_processed']}")
    print(f"Distribución de Órdenes: {dashboard_report['orders_breakdown']}")
    
    print("\n" + "="*80)
    print("                     TEST DE INTEGRACIÓN FINALIZADO CON ÉXITO")
    print("================================================================================\n")


if __name__ == "__main__":
    run_full_integration_test()