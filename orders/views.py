from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from account.models import Cart
from .models import Order, OrderItem
from .forms import OrderCreateForm


@login_required
def order_create(request):

    cart_items = Cart.objects.filter(
        buyer=request.user.buyer
    )

    if not cart_items.exists():
        return redirect('cart:cart_detail')

    if request.method == 'POST':

        form = OrderCreateForm(request.POST)

        if form.is_valid():

            # сохраняем адрес
            address = form.save(commit=False)
            address.buyer = request.user.buyer
            address.save()

            # создаём заказ
            order = Order.objects.create(
                buyer=request.user.buyer,
                address=address
            )

            # создаём товары заказа
            for item in cart_items:

                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=item.product.price,
                    quantity=item.quantity
                )

            # очищаем корзину
            cart_items.delete()

            return render(
                request,
                'orders/order/created.html',
                {'order': order}
            )

    else:
        form = OrderCreateForm()

    total = sum(item.total_price for item in cart_items)

    return render(
        request,
        'orders/order/create.html',
        {
            'form': form,
            'cart_items': cart_items,
            'total': total
        }
    )