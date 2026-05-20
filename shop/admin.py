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

# INLINE ДЛЯ ИЗОБРАЖЕНИЙ
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

# CATEGORY

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

# SUPPLIER
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email']
    search_fields = ['name']

# PRODUCT
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

# PRODUCT IMAGE
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'is_main']

# GENRE
@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ['name']

# AUTHOR
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

# TAG
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ['name']

# BOOK
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

# BOARD GAME
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

# STATIONERY
@admin.register(Stationery)
class StationeryAdmin(admin.ModelAdmin):
    list_display = [
        'product',
        'supplier'
    ]

    search_fields = [
        'product__name'
    ]