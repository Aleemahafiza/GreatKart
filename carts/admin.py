from django.contrib import admin

from carts.models import CartItem, Cart

# Register your models here.
admin.site.register(CartItem)
admin.site.register(Cart)
