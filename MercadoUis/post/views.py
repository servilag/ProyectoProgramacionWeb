from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Producto
from .cart import Cart
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import Producto, Tag, Compra
from .forms import ProductoForm, RegistroUsuarioForm, ReviewForm



@login_required
def nuevo_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES) # request.FILES es CLAVE para la imagen
        if form.is_valid():
            producto = form.save(commit=False)
            producto.author = request.user # Asignamos automáticamente al estudiante logueado
            producto.save()
            form.save_m2m() # Obligatorio para guardar las etiquetas (ManyToMany)
            return redirect('productos_lista') # O la vista que prefieras redirigir (ej: lista de productos)
    else:
        form = ProductoForm()
    
    return render(request, 'post/nuevo_producto.html', {'form': form})

# 2. UPDATE: Editar un producto existente
@login_required
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    
    # Seguridad: Solo el vendedor del producto puede editarlo
    if producto.author != request.user:
        raise PermissionDenied
        
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('detalle_producto', producto_id=producto.id)
    else:
        form = ProductoForm(instance=producto)
        
    return render(request, 'post/editar_producto.html', {'form': form, 'producto': producto})


@login_required
@require_POST
def borrar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
        
        # 🔒 SEGURIDAD MODERADA: El dueño O un administrador pueden borrarlo
    if producto.author == request.user or request.user.is_staff:
            producto.delete()
            
        # Redirige a la página desde donde venía o al perfil
    return redirect(request.META.get('HTTP_REFERER', 'perfil'))

def add_to_cart(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    
    # Obtenemos el carrito de la sesión o creamos uno nuevo
    carrito = request.session.get('carrito', {})
    
    # Agregamos el producto o incrementamos cantidad
    prod_id_str = str(producto.id)
    if prod_id_str in carrito:
        carrito[prod_id_str] += 1
    else:
        carrito[prod_id_str] = 1
        
    # Guardamos de vuelta en la sesión
    request.session['carrito'] = carrito
    request.session.modified = True
    
    return redirect('ver_carrito')

def remove_from_cart(request, producto_id):
    cart = Cart(request)
    producto = get_object_or_404(Producto, id=producto_id)
    cart.remove(producto)
    return redirect('ver_carrito')

def decrement_cart_item(request, producto_id):
    cart = Cart(request)
    producto = get_object_or_404(Producto, id=producto_id)
    cart.decrement(producto)
    return redirect('ver_carrito')

@login_required
def ver_carrito(request):
    carrito_sesion = request.session.get('carrito', {})
    productos_en_carrito = []
    total = 0
    
    for prod_id, cantidad in carrito_sesion.items():
        try:
            producto = Producto.objects.get(id=int(prod_id))
            subtotal = producto.price * cantidad
            total += subtotal
            productos_en_carrito.append({
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': subtotal
            })
        except (Producto.DoesNotExist, ValueError):
            continue

    return render(request, 'post/carrito.html', {'items': productos_en_carrito, 'total': total})


def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id) # (O la función que uses)
    
    # 1. TRAER LOS COMENTARIOS EXISTENTES
    comentarios = producto.comments.all().order_by('-created_at')
    
    # 2. PROCESAR EL FORMULARIO DE NUEVO COMENTARIO
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
            
        form = ReviewForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            
            # --- AQUÍ VA LA MAGIA DEL RATING ⭐️ ---
            # Leemos el valor del <select name="rating"> que pusiste en el HTML
            # y se lo asignamos al nuevo campo del modelo antes de guardar.
            comentario.rating = int(request.POST.get('rating', 5))
            # --------------------------------------
            
            comentario.producto = producto # (Por si acaso mantienes ambas líneas)
            comentario.post = producto # Usamos 'post' porque así se llama tu ForeignKey
            comentario.author = request.user
            
            comentario.save()
            return redirect('detalle_producto', producto_id=producto.id)
            
    else:
        form = ReviewForm()
        
    # Recuerda pasar el form y los comentarios al template al final de tu vista
    return render(request, 'post/detalle_productos.html', {
        'producto': producto,
        'form': form,
        'comentarios': comentarios
    })
#lista
# Modifica la línea 123 en post/views.py
def productos_lista(request):
    # Cambiamos .order_block() por order_by para organizar por ID o fecha de forma descendente
    productos = Producto.objects.all().order_by('-id') 
    productos_recomendados = Producto.objects.filter(on_sale=True).order_by('?')[:4]
    # El resto del código de filtrado se queda exactamente igual:
    query_buscar = request.GET.get('buscar', '')
    tag_seleccionado = request.GET.get('tag', '')

    if query_buscar:
        productos = productos.filter(title__icontains=query_buscar)

    if tag_seleccionado:
        productos = productos.filter(tags__name=tag_seleccionado)

    todos_los_tags = Tag.objects.all()

    context = {
        'productos': productos,
        'tags': todos_los_tags,
        'tag_actual': tag_seleccionado,
        'recomendados': productos_recomendados,
    }
    return render(request, 'post/productos_lista.html', context)

def registro_usuario(request):
    if request.user.is_authenticated:
        return redirect('productos_lista') # Si ya está logueado, lo mandamos a la tienda
        
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login') # Redirige al login tras un registro exitoso
    else:
        form = RegistroUsuarioForm()
    return render(request, 'post/registro.html', {'form': form})

@login_required

def perfil_usuario(request):
    mis_productos = Producto.objects.filter(author=request.user)

    ordenes_crudas = Compra.objects.filter(comprador=request.user).order_by('-fecha_compra')
    
    mis_compras = []
    for orden in ordenes_crudas:
        try:
            producto_obj = Producto.objects.get(id=orden.producto_id)
            titulo_producto = producto_obj.title
        except Producto.DoesNotExist:
            titulo_producto = "Producto no encontrado o eliminado"
            
        mis_compras.append({
            'id': orden.id,
            'producto_titulo': titulo_producto,
            'precio_pagado': orden.precio_pagado,
            'fecha_compra': orden.fecha_compra,
        })
    context = {
        'productos': mis_productos,
        'mis_compras': mis_compras,  
    }
    return render(request, 'post/perfil_usuario.html', context)

@login_required
def procesar_pago(request):
    if request.method == 'POST':
        carrito_sesion = request.session.get('carrito', {})
        
        if not carrito_sesion:
            return redirect('productos_lista')
            
        for prod_id, cantidad in carrito_sesion.items():
            try:
                producto = Producto.objects.get(id=int(prod_id))
                
                Compra.objects.create(
                    comprador=request.user,
                    producto_id=producto.id,
                    precio_pagado=producto.price 
                )
                
                producto.on_sale = False
                producto.save()
                
            except Producto.DoesNotExist:
                continue
                
        request.session['carrito'] = {}
        request.session.modified = True
        
        return render(request, 'post/pago_realizado.html')
        
    return redirect('ver_carrito')

@login_required
def realizar_compra(request, producto_id):
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id=producto_id)
        
        precio_final = producto.price
        
        nueva_compra = Compra.objects.create(
            comprador=request.user,          
            producto_id=producto.id,        
            precio_pagado=precio_final       
        )
        
        producto.on_sale = False
        producto.save()
        
        return redirect('perfil')
        
    return redirect('productos_lista')


def resumen_pago(request):
    carrito = request.session.get('carrito', {})
    productos_en_carrito = []
    total = 0
    
    for prod_id, cantidad in carrito.items():
        try:
            producto = Producto.objects.get(id=int(prod_id))
            subtotal = producto.price * cantidad
            total += subtotal
            productos_en_carrito.append({
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': subtotal
            })
        except (Producto.DoesNotExist, ValueError):
            continue
    return render(request, 'post/resumen_pago.html', {'total': total})