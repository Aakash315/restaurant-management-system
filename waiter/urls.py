from django.urls import path
from . import views

urlpatterns = [
    path('', views.waiter_dashboard, name='waiter_dashboard'),
    path('resolve-request/<int:request_id>/', views.resolve_request, name='resolve_request'),
    path('orders/', views.waiter_orders, name='waiter_orders'),
    path('deliver-item/<int:item_id>/', views.mark_item_delivered, name='mark_item_delivered'),

]