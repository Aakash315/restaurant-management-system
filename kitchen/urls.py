from django.urls import path
from . import views

urlpatterns = [
    path('', views.kitchen_dashboard, name='kitchen_dashboard'),
    path('update-item/<int:item_id>/', views.update_kitchen_status, name='update_kitchen_status'),
]
