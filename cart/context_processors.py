from account.models import Cart
from django.db.models import Sum


def cart(request):

    if request.user.is_authenticated:

        buyer = getattr(request.user, 'buyer', None)

        if buyer:
            count = Cart.objects.filter(
                buyer=buyer
            ).aggregate(
                total=Sum('quantity')
            )['total'] or 0
        else:
            count = 0

    else:
        count = 0

    return {
        'cart_item_count': count
    }