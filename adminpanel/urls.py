from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('menu/', views.menu_management, name='menu_management'),
    path('menu/add', views.add_menu_item, name='add_menu_item'),
    path('menu/edit/<int:item_id>/', views.edit_menu_item, name='edit_menu_item'),
    path('menu/delete/<int:item_id>/', views.delete_menu_item, name='delete_menu_item'),
    path('tables/', views.table_config, name='table_config'),
    path('users/', views.user_management, name='user_management'),
    path('tax-settings/', views.tax_settings, name='tax_settings'),
    path('add-user/', views.add_user, name='add_user'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('add-table/', views.add_table, name='add_table'),

]
