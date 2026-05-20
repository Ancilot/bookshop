from django import forms

from shop.models import (
    Product,
    Book,
    BoardGame,
    Stationery
)


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class ProductForm(forms.ModelForm):

    class Meta:

        model = Product

        fields = [
            'name',
            'price',
            'description',
            'category',
            'available',
        ]



class BookForm(forms.ModelForm):

    class Meta:

        model = Book

        exclude = ['product']


class BoardGameForm(forms.ModelForm):

    class Meta:

        model = BoardGame

        exclude = ['product']


class StationeryForm(forms.ModelForm):

    class Meta:

        model = Stationery

        exclude = ['product']