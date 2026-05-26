from decimal import Decimal
from .models import Producto

class Cart:
    def __init__(self, request):
        """
        Inicializa el carrito usando la sesión del request.
        """
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            # Si no hay carrito en la sesión, creamos uno vacío
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, producto, cantidad=1, update_cantidad=False):
        producto_id = str(producto.id)
        if producto_id not in self.cart:
            self.cart[producto_id] = {
                'quantity': 0,
                'price': str(producto.precio_final) # ¡Aquí usamos de paso el precio con descuento!
            }
        
        if update_cantidad:
            self.cart[producto_id]['quantity'] = cantidad
        else:
            self.cart[producto_id]['quantity'] += cantidad
            
        self.save()

    def remove(self, producto):
        """
        Elimina un producto por completo del carrito.
        """
        producto_id = str(producto.id)
        if producto_id in self.cart:
            del self.cart[producto_id]
            self.save()

    def decrement(self, producto):
        """
        Resta 1 a la cantidad de un producto. Si llega a 0, lo elimina.
        """
        producto_id = str(producto.id)
        if producto_id in self.cart:
            self.cart[producto_id]['cantidad'] -= 1
            if self.cart[producto_id]['cantidad'] <= 0:
                self.remove(producto)
            else:
                self.save()

    def save(self):
        # Marca la sesión como "modificada" para asegurarse de que Django la guarde
        self.session.modified = True

    def clear(self):
        del self.session['cart']
        self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        # Traemos todos los productos que están en el carrito de un solo golpe
        productos = Producto.objects.filter(id__in=product_ids)
        
        # Hacemos una copia del carrito de la sesión para no mutarlo directamente
        cart = self.cart.copy()
        
        # Inyectamos el objeto Producto real en la copia del carrito
        for producto in productos:
            cart[str(producto.id)]['product'] = producto

        # Retornamos los elementos para el bucle del HTML
        for item in cart.values():
            # Nos aseguramos de que el precio sea un entero/float y no un string
            item['price'] = int(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item
        
    def __len__(self):
        # Asegúrate de que use 'quantity' tal como se guarda en la sesión
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(int(item['price']) * item['quantity'] for item in self.cart.values())