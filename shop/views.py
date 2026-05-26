from django.shortcuts import get_object_or_404, redirect, render
from django.core.exceptions import PermissionDenied
from django.db.models import Q

from .models import Product, Category, Review
from orders.models import OrderItem
from .forms import ReviewForm


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    return render(request, 'shop/product/list.html', {
        'category': category,
        'categories': categories,
        'products': products
    })


def search_products(request):
    query = request.GET.get('q')
    products = Product.objects.filter(available=True)

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    return render(request, 'shop/product/search.html', {
        'query': query,
        'products': products,
        'categories': Category.objects.all(),
    })


def product_detail(request, id, slug):

    product = get_object_or_404(
        Product,
        id=id,
        slug=slug,
        available=True
    )

    book = getattr(product, 'book', None)
    board_game = getattr(product, 'board_game', None)
    stationery = getattr(product, 'stationery', None)

    can_review = False
    user_review = None

    if request.user.is_authenticated:
        buyer = getattr(request.user, 'buyer', None)

        if buyer:

            # проверка покупки
            purchased = OrderItem.objects.filter(
                order__buyer=buyer,
                order__paid=True,
                product=product
            ).exists()

            # отзыв пользователя
            user_review = Review.objects.filter(
                product=product,
                buyer=buyer
            ).first()

            # можно оставить отзыв только если купил и ещё не писал
            can_review = purchased and user_review is None

    return render(request, 'shop/product/detail.html', {
        'product': product,
        'book': book,
        'board_game': board_game,
        'stationery': stationery,
        'can_review': can_review,
        'user_review': user_review,
    })

def edit_review(request, review_id):


    review = get_object_or_404(Review, id=review_id)

    buyer = getattr(request.user, 'buyer', None)

    # защита: редактировать может только автор
    if not buyer or review.buyer != buyer:
        raise PermissionDenied("Вы не можете редактировать этот отзыв")

    if request.method == 'POST':

        form = ReviewForm(request.POST, instance=review)

        if form.is_valid():
            form.save()

            return redirect('shop:product_detail',
                            id=review.product.id,
                            slug=review.product.slug)

    else:
        form = ReviewForm(instance=review)

    return render(request, 'shop/review_form.html', {
        'form': form,
        'product': review.product,
        'edit_mode': True
    })


def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    buyer = getattr(request.user, 'buyer', None)

    if not buyer:
        return redirect('account:login')

    # уже есть отзыв?
    review = Review.objects.filter(product=product, buyer=buyer).first()

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.product = product
            obj.buyer = buyer
            obj.save()
            return redirect(product.get_absolute_url())

    else:
        form = ReviewForm(instance=review)

    return render(request, 'shop/review_form.html', {
        'form': form,
        'product': product,
        'review': review,
    })