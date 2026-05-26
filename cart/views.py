from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from shop.models import Product
from django.http import HttpResponseForbidden
from account.models import Cart
from account.models import Buyer

@login_required
def cart_add(request, product_id):

    product = get_object_or_404(Product, id=product_id)
    if not product.available:
        return HttpResponseForbidden("Товар недоступен для покупки")

    quantity = int(request.POST.get('quantity', 1))

    cart_item, created = Cart.objects.get_or_create(
        buyer=request.user.buyer,
        product=product
    )

    if created:
        cart_item.quantity = quantity
    else:
        cart_item.quantity += quantity

    cart_item.save()

    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def cart_remove(request, product_id):
    buyer = request.user.buyer
    Cart.objects.filter(buyer=buyer, product_id=product_id).delete()
    return redirect('cart:cart_detail')


@login_required
def cart_detail(request):
    cart_items = Cart.objects.filter(buyer=request.user.buyer)
    total = sum(item.total_price for item in cart_items)

    return render(request, 'shop/cart/cart.html', {
        'cart_items': cart_items,
        'total': total
    })

def cart_update(request, product_id):

    buyer = request.user.buyer

    cart_item = get_object_or_404(
        Cart,
        buyer=buyer,
        product_id=product_id
    )

    action = request.POST.get('action')

    if action == 'increase':
        cart_item.quantity += 1

    elif action == 'decrease':

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
        else:
            cart_item.delete()
            return redirect('cart:cart_detail')

    cart_item.save()

    return redirect('cart:cart_detail')