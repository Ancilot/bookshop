from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.product_list, name='product_list'),

    path('search/', views.search_products, name='search_products'),
    path('product/<int:product_id>/review/', views.add_review, name='add_review'),
    path('review/<int:review_id>/edit/', views.edit_review, name='edit_review'),

    path('<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),

    path('<slug:category_slug>/', views.product_list, name='product_list_by_category'),
]
