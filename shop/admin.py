from django.contrib import admin
from .models import (
    Category,
    Supplier,
    Product,
    ProductImage,
    Genre,
    Author,
    Tag,
    Book,
    BoardGame,
    Stationery
)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email']
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'category',
        'price',
        'available',
        'created'
    ]

    list_filter = [
        'available',
        'created',
        'updated',
        'category'
    ]

    list_editable = [
        'price',
        'available'
    ]

    search_fields = [
        'name',
        'description'
    ]

    prepopulated_fields = {
        'slug': ('name',)
    }

    inlines = [ProductImageInline]

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'is_main']

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ['name']

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = [
        'last_name',
        'first_name',
        'middle_name'
    ]

    search_fields = [
        'last_name',
        'first_name'
    ]

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ['name']

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = [
        'product',
        'publisher',
        'year',
        'isbn'
    ]

    list_filter = [
        'year',
        'publisher'
    ]

    search_fields = [
        'product__name',
        'isbn'
    ]

    filter_horizontal = [
        'authors',
        'genres',
        'tags'
    ]

@admin.register(BoardGame)
class BoardGameAdmin(admin.ModelAdmin):
    list_display = [
        'product',
        'audience',
        'year',
        'publisher'
    ]

    list_filter = [
        'year',
        'publisher'
    ]

    search_fields = [
        'product__name'
    ]

    filter_horizontal = [
        'genres'
    ]

@admin.register(Stationery)
class StationeryAdmin(admin.ModelAdmin):
    list_display = [
        'product',
        'supplier'
    ]

    search_fields = [
        'product__name'
    ]