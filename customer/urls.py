from django.urls import path
from . import views

urlpatterns = [
    path('', views.customer_register, name='customer_register'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('enter-members/', views.enter_members, name='enter_members'),
    path('menu/', views.menu_view, name='menu_view'), 
    # path('menu/item/<int:item_id>/', views.menu_item_detail, name='menu_item_detail'),   
    path('cart/', views.view_cart, name='view_cart'),
    path('place-order/', views.place_order, name='place_order'),
    path('request-assistance/', views.request_assistance, name='request_assistance'),
    path('request-bill/', views.request_bill, name='request_bill'),
    path('submit-tip/', views.submit_tip, name='submit_tip'),
    path('order-status/', views.order_status, name='order_status'),
    path('feedback/', views.leave_feedback, name='leave_feedback'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/increase/<int:item_id>/', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:item_id>/', views.decrease_quantity, name='decrease_quantity'), 
    path('start-payment/', views.start_payment, name='start_payment'),
    path('payment-success/', views.payment_success, name='payment_success'),   

]
