from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # товары
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:id>/edit/', views.product_update, name='product_update'),
    path('products/<int:id>/delete/', views.product_delete, name='product_delete'),

    # отчеты
    path('reports/', views.reports, name='reports'),

    # экспорт
    path('reports/excel/', views.export_excel, name='export_excel'),
    path('reports/pdf/', views.export_pdf, name='export_pdf'),
    path('ajax/load-category-form/',views.load_category_form,name='load_category_form'),
]