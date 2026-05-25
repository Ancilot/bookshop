from django.db import models
from django.urls import reverse
from django.db.models import Q, UniqueConstraint
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.utils.timezone import now
from transliterate import translit
from django.utils.text import slugify

class Price(models.Model):
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='prices',
        verbose_name='Товар'
    )

    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Цена'
    )

    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"{self.value}"

class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="Категория")
    slug = models.SlugField(max_length=200, unique=True, blank=True) # slug — это URL-версия названия.name	slug
                                                                        # Детективы	detective

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_list_by_category', args=[self.slug])



class Supplier(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")

    class Meta:
        verbose_name = "Поставщик"
        verbose_name_plural = "Поставщики"

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="Товар"
    )
    image = models.ImageField(
        upload_to='products/%Y/%m/%d',
        verbose_name="Изображение"
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name="Главное изображение"
    )

    class Meta:
        ordering = ['-is_main']
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товаров"

        constraints = [
            UniqueConstraint(
                fields=['product'],
                condition=Q(is_main=True),
                name='unique_main_image_per_product'
            )
        ]


    def __str__(self):
        return f"{self.product.name} - {self.id}"




class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name="Описание")
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,blank=False, null=False,
        related_name='products',
        verbose_name="Категория"
    )
    available = models.BooleanField(default=True, verbose_name="Доступен для продажи")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_price_value(self):
        price = self.prices.first()
        return price.value if price else None

    @property
    def price(self):
        return self.get_price_value()

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.id, self.slug])

    def get_main_image(self):
        return self.images.filter(is_main=True).first()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug()

        super().save(*args, **kwargs)

    def generate_unique_slug(self):
        base_slug = slugify(self.name, allow_unicode=True)
        slug = base_slug
        counter = 1

        # исключаем текущий объект при update
        qs = Product.objects.all()

        if self.pk:
            qs = qs.exclude(pk=self.pk)

        while qs.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug



class Genre(models.Model):
    name = models.CharField(max_length=100, verbose_name="Жанр")

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    def __str__(self):
        return self.name


class Author(models.Model):
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    middle_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Отчество")

    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"
        ordering = ['last_name', 'first_name']

    def __str__(self):
        if self.middle_name:
            return f"{self.last_name} {self.first_name} {self.middle_name}"
        return f"{self.last_name} {self.first_name}"


class Tag(models.Model):
    name = models.CharField(max_length=100, verbose_name="Тег", unique=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Book(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='book',
        verbose_name="Товар"
    )
    authors = models.ManyToManyField(Author, blank=False, verbose_name="Авторы")
    genres = models.ManyToManyField(Genre, blank=True, verbose_name="Жанры")
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="Теги")
    publisher = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name="Издательство")
    year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(now().year)
        ],
        verbose_name="Год издания"
    )

    pages = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        verbose_name="Страниц"
    )

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"

    def __str__(self):
        return self.product.name


class BoardGame(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='board_game',
        verbose_name="Товар"
    )
    genres = models.ManyToManyField(Genre, blank=True, verbose_name="Жанры")
    audience = models.CharField(max_length=100, verbose_name="Целевая аудитория")
    year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(now().year)
        ],
        verbose_name="Год издания"
    )
    publisher = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name="Издательство")

    class Meta:
        verbose_name = "Настольная игра"
        verbose_name_plural = "Настольные игры"

    def __str__(self):
        return self.product.name


class Stationery(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='stationery',
        verbose_name="Товар"
    )
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE,blank=True,null=True, verbose_name="Поставщик")

    class Meta:
        verbose_name = "Канцелярский товар"
        verbose_name_plural = "Канцелярские товары"

    def __str__(self):
        return self.product.name