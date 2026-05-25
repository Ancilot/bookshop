from django import forms
from shop.models import Product, Book, BoardGame, Stationery, Price
from django.utils.timezone import now

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