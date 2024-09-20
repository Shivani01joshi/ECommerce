from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    
    path('register/',views.Sign_up,name='signUp'),
    path('login/',views.user_login,name='login'),
    path('logout/',views.user_logout,name='logout'),
    path('verify_otp/',views.verify_otp,name='verify_otp'),
    path('verify_otp_login/',views.verify_otp_login,name='verify_otp_login'),
    path('forget_password/',views.forget_password,name='forget_password'),
    path('verify_otp_forget_password/',views.verify_otp_forget_password,name='verify_otp_forget_password'),
     path('Reset_password/',views.Reset_password,name='Reset_password'),
    path('change_password/',views.change_password,name='change_password'),
    path('product/',views.product,name='product'),
    #path('product/<int:id>/', views.get_product, name='product_detail'),
     path('add_category',views.add_category,name='add_category'),
    path('add_product',views.add_product,name='add_product'),
    path('products/<int:product_id>/edit/', views.update_product, name='update_product'),
    path('products/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('cart/<int:pk>/',views.add_to_cart,name='add_to_cart'),
    path('cart/', views.view_cart, name='cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout_page, name='checkout'),
    #path('', views.product_list, name='product_list'),
    #path('payment/', views.payment, name='payment'),
   # Example URL pattern in urls.py
     path('my-orders/', views.user_orders, name='user_orders'),
     path('orders/', views.particular_orders, name='particular_orders'),
    path('create-payment-intent/', views.create_payment_intent, name='create_payment_intent'),
    path('payment-confirm/<str:payment_intent_id>/', views.payment_confirm, name='payment_confirm'),
    path('confirm-payment/', views.confirm_payment, name='confirm_payment'),
    path('cancel-payment/', views.cancel_payment, name='cancel'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
   path('scan_order/',views.scan_order,name='scan_order'),
   path('shippment-status/<int:id>/',views.shippment_status,name='shippment-status'),
   
    
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
