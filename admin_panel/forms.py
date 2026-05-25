from django import forms
from django.db.models.functions import Lower

from shop.models import Product, Book, BoardGame, Stationery, Price, Genre, Author, Tag, Supplier
from django.utils.timezone import now
import re
from django.core.exceptions import ValidationError

class GenreForm(forms.ModelForm):
    class Meta:
        model = Genre
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data.get('name')

        if name:
            name = name.strip()

        normalized = name.casefold()

        for genre in Genre.objects.all():
            if genre.name.casefold() == normalized:
                raise forms.ValidationError(
                    "Такой жанр уже существует"
                )

        return name

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['last_name', 'first_name', 'middle_name']

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data.get('name')

        if name:
            name = name.strip()

        normalized = name.casefold()

        for tag in Tag.objects.all():
            if tag.name.casefold() == normalized:
                raise forms.ValidationError(
                    "Такой тег уже существует"
                )

        return name

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'phone', 'email']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        if not phone:
            return phone

        # только цифры
        if not phone.isdigit():
            raise ValidationError("Телефон должен содержать только цифры")

        # длина
        if len(phone) != 11:
            raise ValidationError("Телефон должен содержать 11 цифр")

        # первая цифра
        if phone[0] not in ('7', '8'):
            raise ValidationError("Телефон должен начинаться с 7 или 8")

        return phone

CURRENT_YEAR = now().year

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name',
            'description',
            'category',
            'available'
        ]


class PriceForm(forms.ModelForm):
    class Meta:
        model = Price
        fields = ['value']

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        exclude = ['product']

        widgets = {
            'year': forms.NumberInput(attrs={
                'min': 0,
                'max': CURRENT_YEAR,
                'step': 1,
                'maxlength': 4,
                'inputmode': 'numeric',
                'pattern': '[0-9]*',
            }),

            'pages': forms.NumberInput(attrs={
                'min': 1,
                'step': 1,
                'maxlength': 5,
                'inputmode': 'numeric',
                'pattern': '[0-9]*',
            })
        }

    def clean_year(self):
        year = self.cleaned_data.get('year')

        if year and year > CURRENT_YEAR:
                raise forms.ValidationError(
                    f'Год издания не может быть больше {CURRENT_YEAR}'
                )

        return year

    def clean_pages(self):
        pages = self.cleaned_data.get('pages')

        if pages and pages < 1:
                raise forms.ValidationError(
                    'Количество страниц должно быть больше 0'
                )

        return pages


class BoardGameForm(forms.ModelForm):
    class Meta:
        model = BoardGame
        exclude = ['product']

        widgets = {
            'year': forms.NumberInput(attrs={
                'min': 0,
                'max': CURRENT_YEAR,
                'step': 1,
                'maxlength': 4,
                'inputmode': 'numeric',
                'pattern': '[0-9]*',
            })
        }

    def clean_year(self):
        year = self.cleaned_data.get('year')

        if year and year > CURRENT_YEAR:
                raise forms.ValidationError(
                    f'Год издания не может быть больше {CURRENT_YEAR}'
            )

        return year


class StationeryForm(forms.ModelForm):
    class Meta:
        model = Stationery
        exclude = ['product']