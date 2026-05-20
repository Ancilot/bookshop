from django.shortcuts import get_object_or_404, redirect
from shop.models import Product
from account.models import Cart
from django.contrib.auth.decorators import login_required

@login_required
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    buyer = request.user.buyer

    cart_item, created = Cart.objects.get_or_create(
        buyer=buyer,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('shop:product_detail', id=product.id, slug=product.slug)
@login_required
def cart_remove(request, product_id):
    buyer = request.user.buyer
    Cart.objects.filter(buyer=buyer, product_id=product_id).delete()
    return redirect('account:cart_detail')
@login_required
def cart_detail(request):
    cart_items = Cart.objects.filter(buyer=request.user.buyer)

    total = sum(item.total_price for item in cart_items)

    return render(request, 'account/cart.html', {
        'cart_items': cart_items,
        'total': total
    })