from django.db import models
from account.models import Buyer, Address
from shop.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В обработке'),
        ('paid', 'Оплачен'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    ]

    buyer = models.ForeignKey(
        Buyer,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Покупатель'
    )

    address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Адрес доставки'
    )

    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата заказа'
    )

    updated = models.DateTimeField(
        auto_now=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )

    paid = models.BooleanField(
        default=False,
        verbose_name='Оплачен'
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created']

    def __str__(self):
        return f'Заказ #{self.id}'

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Заказ'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name='Товар'
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена на момент покупки'
    )

    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'

    @property
    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f'{self.product.name} ({self.quantity})'