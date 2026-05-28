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
    path('products/<int:id>/restore/', views.product_restore, name='product_restore'),

    # отчеты
    path('reports/', views.reports, name='reports'),

    # экспорт
    path('reports/excel/', views.export_excel, name='export_excel'),
    path('ajax/load-category-form/',views.load_category_form,name='load_category_form'),

    # Справочники
    path('dictionaries/', views.dictionaries, name='dictionaries'),
    # Genres
    path('genres/', views.genre_list, name='genre_list'),
    path('genres/create/', views.genre_create, name='genre_create'),
    path('genres/<int:id>/delete/', views.genre_delete, name='genre_delete'),

    # Authors
    path('authors/', views.author_list, name='author_list'),
    path('authors/create/', views.author_create, name='author_create'),
    path('authors/<int:id>/delete/', views.author_delete, name='author_delete'),

    # Tags
    path('tags/', views.tag_list, name='tag_list'),
    path('tags/create/', views.tag_create, name='tag_create'),
    path('tags/<int:id>/delete/', views.tag_delete, name='tag_delete'),

    # Suppliers
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:id>/delete/', views.supplier_delete, name='supplier_delete'),
    path('suppliers/<int:id>/restore/', views.supplier_restore, name='supplier_restore'),
    ]