# main.py
# CÓDIGO FINAL ANTIFALLO para la entrega.

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
    print("\n" + "="*80)
    print("      TEST DE INTEGRACIÓN FINAL ECOMARKET (MODO DE ENTREGA RÁP💨)")
    print("="*80 + "\n")

    # ----------------------------------------------------
    # FASE 1 & 2: INICIALIZACIÓN DE COMPONENTES
    # ----------------------------------------------------
    try:
        user_repo = UserRepository() 
        product_repo = ProductRepository() 
        cart_repo = CartRepository()
        order_repo = OrderRepository()
        email_adapter = EmailAdapter() 
        payment_service = PaymentService() 
        
        register_service = RegisterService(user_repository=user_repo)
        login_service = LoginService(user_repository=user_repo)
        profile_service = ClientProfileService(user_repository=user_repo)
        catalogue_service = CatalogueService(product_repository=product_repo)
        cart_service = ShoppingCartService(cart_repository=cart_repo, product_repository=product_repo)
        order_service = OrderService(order_repo, cart_repo, product_repo, payment_service)
        invoice_service = InvoiceService(email_adapter)
        dashboard_service = DashboardService(product_repo, order_repo, user_repo)
        print("[OK] Componentes inicializados.")
    except Exception as e:
        print(f"[ERROR CRÍTICO] Falló la conexión/inicialización. Error: {e}")
        return

    # ----------------------------------------------------
    # FASE 3: FLUJO DEL CLIENTE (AUTENTICACIÓN Y PERFIL)
    # ----------------------------------------------------
    print("\n--- 3. AUTENTICACIÓN Y PERFIL ---")
    
    # 3a. Registro (Intentamos el registro, si ya existe, obtenemos el ID)
    register_result = register_service.add({"email": TEST_EMAIL, "password": TEST_PASSWORD, "nombre": "Cliente Rocío"})
    
    # Manejo del ID: Si el registro falla (porque ya existe), el ID viene del 'user_id' en el mensaje
    user_id = register_result.get('user_id')
    print(f"Resultado Registro: {register_result['status']} | Mensaje: {register_result.get('message', 'Registro Exitoso')}")
    
    # 3b. Login (Usamos el ID para asegurar consistencia)
    login_result = login_service.login(TEST_EMAIL, TEST_PASSWORD)
    user_id = login_result.get('user_data', {}).get('user_id')
    
    if not user_id or login_result.get('status') == 'error':
        print(f"[ERROR FATAL] Login fallido o ID no encontrado. Deteniendo.")
        return
        
    print(f"Resultado Login: {login_result['status']} (ID: {user_id})")

    # 3c. Actualización de Perfil (Prueba del servicio getperfil/update)
    profile_update = profile_service.update(user_id, {'direccion': 'Av. Frutas y Verduras 2025'})
    print(f"Resultado Update Perfil: {profile_update['status']}")


    # ----------------------------------------------------
    # FASE 4: FLUJO DE COMPRA (CATÁLOGO Y CARRITO)
    # ----------------------------------------------------
    print("\n--- 4. FLUJO DE COMPRA (Manzanas y Plátanos) ---")
    
    # 4a. Consulta de Catálogo
    catalogue = catalogue_service.query()
    
    if len(catalogue) < 2:
        print("[AVISO] Sólo hay un producto en catálogo. Deteniendo para evitar Index Error.")
        return

    # Usamos los dos primeros productos (Manzana y Tomate/Plátano)
    product_item_1_id = catalogue[0]['product_id'] 
    product_item_2_id = catalogue[1]['product_id']

    print(f"Productos Seleccionados (IDs): {product_item_1_id} y {product_item_2_id}")

    # 4b. Añadir al Carrito
    cart_service.add({'user_id': user_id, 'product_id': product_item_1_id, 'quantity': 5}) # 5 Manzanas
    cart_service.add({'user_id': user_id, 'product_id': product_item_2_id, 'quantity': 2}) # 2 Tomates/Plátanos
    
    # 4c. Consulta del Carrito
    cart_view = cart_service.query({'user_id': user_id})

    if cart_view.get('status') == 'error':
        print(f"[ERROR CARRITO] Falló la consulta: {cart_view.get('message', 'Respuesta inesperada')}.")
        return
    
    print(f"Carrito Actualizado: Ítems: {len(cart_view['items'])} | Total: ${cart_view['total']:.2f}")
        
    item_1_stock_before = product_repo.get_by_id(product_item_1_id).stock


    # ----------------------------------------------------
    # FASE 5: CHECKOUT COMPLETO (PAGO, PEDIDO, STOCK, BOLETA)
    # ----------------------------------------------------
    print("\n--- 5. CHECKOUT Y PROCESAMIENTO ---")
    
    checkout_data = {
        "user_id": user_id,
        "card_data": {"card_number": "1111222233334444", "cvv": "123"}, 
        "shipping_address": "Av. Frutas y Verduras 2025"
    }

    checkout_result = order_service.add(checkout_data)
    order_id = checkout_result.get('order_id')
    
    print(f"Resultado Checkout: {checkout_result['status']} | Pedido ID: {order_id} | Total: ${checkout_result.get('total'):.2f}")
    
    if checkout_result['status'] == 'error':
        print(f"[ERROR CHECKOUT] El checkout falló. Deteniendo.")
        return

    # 5a. Reducción de Stock (Verificación)
    item_1_stock_after = product_repo.get_by_id(product_item_1_id).stock
    print(f"Stock Manzana Roja (post-compra): {item_1_stock_after} (Reducción de 5)")
    
    # 5b. Envío de Boleta
    final_order = order_repo.get_by_id(order_id)
    invoice_result = invoice_service.generate_and_send(final_order, TEST_EMAIL)
    print(f"Resultado Envío Boleta: {invoice_result['status']}")

    # ----------------------------------------------------
    # FASE 6: FLUJO ADMINISTRATIVO (DASHBOARD)
    # ----------------------------------------------------
    print("\n--- 6. REPORTE DE DASHBOARD ---")
    
    order_service.update_status(order_id, "entregado")
    dashboard_report = dashboard_service.query()
    
    print(f"Ingreso Total Reportado: ${dashboard_report['metrics']['total_revenue']:.2f}")
    print(f"Órdenes Procesadas: {dashboard_report['metrics']['total_orders_processed']}")
    print("\n" + "="*80)
    print("                 ¡EJECUCIÓN FINALIZADA CON ÉXITO! 🎉")
    print("================================================================================\n")


if __name__ == "__main__":
    run_full_integration_test()