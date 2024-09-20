from django.contrib import admin
from .models import  Category, Order, OrderItem, Product, Rating, checkoutAddress  # Import your Product model

# Register your models here.
@admin.register(Product)  
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price')

@admin.register(Category)  
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

admin.site.register(Order)
admin.site.register(Rating)
admin.site.register(OrderItem)
admin.site.register(checkoutAddress)





