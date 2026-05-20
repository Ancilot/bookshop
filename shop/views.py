from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from django.db.models import Q

def product_list(request, category_slug=None):
    category = None

    categories = Category.objects.all()

    products = Product.objects.filter(
        available=True
    )

    if category_slug:
        category = get_object_or_404(
            Category,
            slug=category_slug
        )

        products = products.filter(
            category=category
        )

    context = {
        'category': category,
        'categories': categories,
        'products': products
    }

    return render(
        request,
        'shop/product/list.html',
        context
    )


def product_detail(request, id, slug):
    product = get_object_or_404(
        Product,
        id=id,
        slug=slug,
        available=True
    )

    board_game = getattr(product, 'board_game', None)
    stationery = getattr(product, 'stationery', None)
    book = getattr(product, 'book', None)
    context = {
        'product': product,
        'book': book,
        'board_game': board_game,
        'stationery': stationery,
    }

    return render(
        request,
        'shop/product/detail.html',
        context
    )
def search_products(request):

    query = request.GET.get('q')

    products = Product.objects.filter(
        available=True
    )

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    categories = Category.objects.all()

    context = {
        'query': query,
        'products': products,
        'categories': categories,
    }

    return render(
        request,
        'shop/product/search.html',
        context
    )