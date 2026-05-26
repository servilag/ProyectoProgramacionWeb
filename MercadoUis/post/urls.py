from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/add/<int:producto_id>/', views.add_to_cart, name='add_to_cart'),
    path('carrito/remove/<int:producto_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('carrito/decrement/<int:producto_id>/', views.decrement_cart_item, name='decrement_cart_item'),
    path('productos/', views.productos_lista, name='productos_lista'),
    path('producto/nuevo/', views.nuevo_producto, name='nuevo_producto'),
    path('producto/<int:producto_id>/editar/', views.editar_producto, name='editar_producto'),
    path('producto/<int:producto_id>/borrar/', views.borrar_producto, name='borrar_producto'),
    path('registro/', views.registro_usuario, name='registro'),
    path('login/', auth_views.LoginView.as_view(template_name='post/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('perfil/', views.perfil_usuario, name='perfil'),
    path('carrito/pago/', views.procesar_pago, name='procesar_pago'),
    path('producto/detalles/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('producto/compra/<int:producto_id>/', views.realizar_compra, name='realizar_compra' )
]
