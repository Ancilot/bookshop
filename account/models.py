from django.db import models
from django.contrib.auth.models import User
from shop.models import Product

class Buyer(models.Model):
    photo = models.ImageField(
        upload_to='users/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name='Фото'
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name='buyer'
    )
    middle_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Отчество")
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Телефон"
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Покупатель"
        verbose_name_plural = "Покупатели"
        ordering = ['user__last_name', 'user__first_name']

    def __str__(self):
        full_name = f"{self.user.last_name} {self.user.first_name}"

        if self.middle_name:
            full_name += f" {self.middle_name}"

        return full_name


class Address(models.Model):
    country = models.CharField(max_length=100, verbose_name="Страна")
    region = models.CharField(max_length=100, verbose_name="Регион")
    city = models.CharField(max_length=100, verbose_name="Город")
    street = models.CharField(max_length=100, verbose_name="Улица")
    house = models.CharField(max_length=20, verbose_name="Дом")
    buyer = models.ForeignKey(
        'Buyer',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='addresses',
        verbose_name="Покупатель"
    )

    class Meta:
        verbose_name = "Адрес"
        verbose_name_plural = "Адреса"

    def __str__(self):
        return f"{self.city}, {self.street} {self.house}"

class Wishlist(models.Model):
    buyer = models.ForeignKey(
        Buyer,
        on_delete=models.CASCADE,
        related_name='wishlist',
        verbose_name="Покупатель"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='in_wishlists',
        verbose_name="Товар"
    )

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        unique_together = ['buyer', 'product']

    def __str__(self):
        return f"{self.buyer} - {self.product.name}"

class Cart(models.Model):
    buyer = models.ForeignKey(
        Buyer,
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name="Покупатель"
    )

    product = models.ForeignKey(
        'shop.Product',
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name="Товар"
    )

    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="Количество"
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"
        unique_together = ['buyer', 'product']

    @property
    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.buyer} - {self.product.name}"