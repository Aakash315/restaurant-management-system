from django.urls import path
from . import views

urlpatterns = [
    path('', views.manager_dashboard, name='manager_dashboard'),
    path('feedback/', views.feedback_list, name='manager_feedback'),
    path('report/', views.daily_report, name='manager_report'),
    path('inventory/', views.inventory_dashboard, name='inventory_dashboard'),
    path('update-stock/<int:item_id>/', views.update_stock, name='update_stock'),
    path('report/export/', views.export_daily_report_csv, name='export_daily_report_csv'),

]
