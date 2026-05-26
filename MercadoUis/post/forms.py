from django import forms
from .models import Producto, Review
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['title', 'content', 'price', 'discount', 'image', 'tags', 'on_sale']
        
        labels = {
            'title': 'Título del Producto',
            'content': 'Descripción o Detalles',
            'price': 'Precio (COP)',
            'discount': 'Descuento (%)',
            'image': 'Imagen del Producto',
            'tags': 'Categorías / Etiquetas',
            'on_sale': '¿Está disponible para la venta?',
        }
        widgets = {
            'tags': forms.CheckboxSelectMultiple(), # Transforma la lista en casillas individuales
        }
        
class RegistroUsuarioForm(UserCreationForm):
    # Forzamos a que estos campos sean obligatorios en el formulario
    first_name = forms.CharField(max_length=30, label="Nombre")
    last_name = forms.CharField(max_length=30, label="Apellido")
    email = forms.EmailField(max_length=254, label="Correo Electrónico")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

# En tu post/forms.py (revisa si lo tienes configurado de esta forma)
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['content'] # <-- Deja solo 'content' para que Django no dibuje un input feo de número