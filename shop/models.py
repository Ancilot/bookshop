from django.db import models
from django.urls import reverse
from django.db.models import Q, UniqueConstraint


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
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    description = models.TextField(blank=True, verbose_name="Описание")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Категория"
    )
    available = models.BooleanField(default=True, verbose_name="Доступен")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.id, self.slug])

    def get_main_image(self):
        return self.images.filter(is_main=True).first()


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
    authors = models.ManyToManyField(Author, blank=True, verbose_name="Авторы")
    genres = models.ManyToManyField(Genre, blank=True, verbose_name="Жанры")
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="Теги")
    publisher = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name="Издательство")
    year = models.IntegerField(verbose_name="Год издания")
    pages = models.IntegerField(blank=True, null=True, verbose_name="Страниц")
    isbn = models.CharField(max_length=20, blank=True, verbose_name="ISBN")

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
    year = models.IntegerField(verbose_name="Год издания")
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
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name="Поставщик")

    class Meta:
        verbose_name = "Канцелярский товар"
        verbose_name_plural = "Канцелярские товары"

    def __str__(self):
        return self.product.name