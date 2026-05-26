from django.db import models
# Importante para poder referenciar el modelo de auth_user
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Modelo de la tabla Categoria / Etiqueta
class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags" # Para que en el admin de Django salga bien escrito

    def __str__(self):
        return self.name


# Modelo de la tabla Post / Producto
class Producto(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField() # Podrías cambiarlo a 'description' si prefieres algo más e-commerce
    author = models.ForeignKey(User, on_delete=models.CASCADE) # El vendedor
    image = models.ImageField(upload_to='post_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    on_sale = models.BooleanField(default=True, verbose_name="¿Está disponible para la venta?")
    discount = models.PositiveIntegerField(default=0, blank=True) # Corregido con default
    tags = models.ManyToManyField(Tag, blank=True) # Relación ManyToMany
    price = models.PositiveIntegerField()

    @property
    def precio_final(self):
        if self.discount > 0:
            # Calcula el descuento y resta al precio original
            descuento = (self.price * self.discount) / 100
            return int(self.price - descuento) # Retorna como entero para que no salgan decimales
        return self.price

    def __str__(self):
        return self.title


# Modelo de la tabla Reseña / Comentario
class Review(models.Model):
    post = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # El nuevo campo para las estrellas ⭐️
    rating = models.PositiveIntegerField(
        default=5, 
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    def __str__(self):
        return f"{self.author.username} - {self.rating}⭐️"

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Carrito de {self.user.username}"

    # Método útil para calcular el total del carrito directamente en el modelo
    @property
    def total_price(self):
        return sum(item.total_item_price for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.producto.title}"

    @property
    def total_item_price(self):
        # Calcula el precio teniendo en cuenta el descuento si existe
        if self.producto.discount > 0:
            price_with_discount = self.producto.price * (1 - (self.producto.discount / 100))
            return price_with_discount * self.quantity
        return self.producto.price * self.quantity
    
# Agregar al final de post/models.py

class Compra(models.Model):
    comprador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='compras')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    precio_pagado = models.PositiveIntegerField()
    fecha_compra = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Orden"
        verbose_name_plural = "Ordenes"

    def __str__(self):
        return f"{self.comprador.username} compró {self.producto.title}"
    