# app/application/services/shopping_cart.py

from app.domain.interfaces.i_crud import ICRUD
from app.infrastructure.repositories.cart_repository import CartRepository
from app.infrastructure.repositories.product_repository import ProductRepository
from app.domain.entities.cart import Cart, CartItem
from typing import Dict, Any, List, Optional
import json

class ShoppingCartService(ICRUD):
    """
    Clase que implementa la lógica ICRUD para la gestión del Carrito de Compras (Historia B-03).
    Demuestra la interacción entre diferentes repositorios.
    """
    def __init__(self, cart_repository: CartRepository, product_repository: ProductRepository):
        # Inyección de dependencias de repositorios
        self.cart_repo = cart_repository
        self.product_repo = product_repository


    # HELPERS (Lógica de Negocio)
    
    def _get_cart_for_user(self, user_id: int) -> Cart:
        """
        Obtiene el carrito existente o crea uno nuevo para el usuario.
        """
        cart = self.cart_repo.get_by_user_id(user_id)
        if not cart:
            cart = Cart(user_id=user_id, items=[])
        return cart

    def _calculate_total(self, cart: Cart) -> float:
        """
        Calcula el precio total del carrito (Lógica de Negocio/Promociones).
        """
        total = sum(item.quantity * item.price_unit for item in cart.items)
        # Aquí se aplicaría la lógica de 'Promociones' si existiera el servicio.
        # total = total - PromotionsService.apply_discounts(total, cart) 
        return round(total, 2)
        
        
    # IMPLEMENTACIÓN DEL CONTRATO ICRUD
    

    def add(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        [CREATE/UPDATE] Añade o actualiza la cantidad de un ítem en el carrito (Historia B-03).
        """
        user_id = input_data['user_id']
        product_id = input_data['product_id']
        quantity_to_add = input_data['quantity']

        # 1. Validar producto y stock (interacción con ProductRepository)
        product = self.product_repo.get_by_id(product_id)
        if not product or product.estado != 'activo':
            return {"status": "error", "message": f"Producto ID {product_id} no válido o inactivo."}
        
        if quantity_to_add <= 0:
            return self.delete(user_id, product_id) # Si se añade 0 o menos, es una eliminación

        # 2. Obtener el carrito del usuario (CartRepository)
        cart = self._get_cart_for_user(user_id)
        
        # 3. Verificar stock disponible total (Lógica de Negocio)
        current_quantity = next((item.quantity for item in cart.items if item.product_id == product_id), 0)
        new_total_quantity = current_quantity + quantity_to_add

        if new_total_quantity > product.stock:
            return {"status": "error", "message": f"Stock insuficiente para {product.nombre}. Disponible: {product.stock}"}

        # 4. Actualizar/Añadir el ítem
        item_index = next((i for i, item in enumerate(cart.items) if item.product_id == product_id), -1)

        if item_index != -1:
            # Actualiza ítem existente
            cart.items[item_index].quantity = new_total_quantity
        else:
            # Añade nuevo ítem
            new_item = CartItem(
                product_id=product_id, 
                quantity=quantity_to_add, 
                price_unit=product.precio_float # Guarda el precio actual del catálogo
            )
            cart.items.append(new_item)

        # 5. Guardar el carrito actualizado y calcular el total
        cart.total_price = self._calculate_total(cart)
        self.cart_repo.save(cart)

        return {"status": "success", "cart_id": cart.cart_id, "total": cart.total_price, "message": "Producto añadido/actualizado en el carrito."}

    def query(self, query_params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        [READ] Consulta el contenido del carrito de un usuario.
        """
        user_id = query_params.get('user_id')
        if not user_id:
            return {"status": "error", "message": "Se requiere 'user_id' para consultar el carrito."}

        cart = self.cart_repo.get_by_user_id(user_id)
        if not cart:
            return {"status": "empty", "message": "El carrito está vacío."}
            
        # Aseguramos que el total esté actualizado antes de mostrar
        cart.total_price = self._calculate_total(cart)
        
        # Convertir a formato legible para la API
        cart_data = cart.__dict__.copy()
        cart_data['items'] = [item.__dict__ for item in cart_data['items']]
        
        return cart_data

    def update(self, key: Any, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        [UPDATE] Reemplaza la cantidad de un ítem en el carrito o lo elimina.
        """
        user_id = key # Aquí 'key' es el user_id
        product_id = input_data['product_id']
        new_quantity = input_data['quantity']
        
        cart = self._get_cart_for_user(user_id)
        
        # 1. Eliminar si la cantidad es cero o menos
        if new_quantity <= 0:
            return self.delete(user_id, product_id)
            
        # 2. Validar stock (similar al método add)
        product = self.product_repo.get_by_id(product_id)
        if not product or new_quantity > product.stock:
            return {"status": "error", "message": f"Stock insuficiente o producto no válido."}

        # 3. Reemplazar la cantidad del ítem
        item_found = False
        for item in cart.items:
            if item.product_id == product_id:
                item.quantity = new_quantity
                item_found = True
                break
                
        if not item_found:
            return {"status": "error", "message": "El producto no estaba en el carrito para actualizar."}

        # 4. Guardar y calcular total
        cart.total_price = self._calculate_total(cart)
        self.cart_repo.save(cart)
        
        return {"status": "success", "cart_id": cart.cart_id, "total": cart.total_price, "message": "Cantidad de producto actualizada."}


    def delete(self, key: Any, product_id: Optional[int] = None) -> bool:
        """
        [DELETE] Elimina un ítem específico del carrito o todo el carrito.
        key: user_id
        product_id: ID del producto a eliminar. Si es None, borra todo el carrito.
        """
        user_id = key
        cart = self._get_cart_for_user(user_id)
        
        # Si no se proporciona product_id, borra todo el carrito
        if product_id is None:
            return self.cart_repo.delete(cart.cart_id) # Borra todo el carrito
            
        # Si se proporciona product_id, borra solo el ítem
        original_count = len(cart.items)
        cart.items[:] = [item for item in cart.items if item.product_id != product_id]
        
        # Si se eliminó algo, actualiza el total y guarda
        if len(cart.items) < original_count:
            cart.total_price = self._calculate_total(cart)
            self.cart_repo.save(cart)
            return True
            
        return False