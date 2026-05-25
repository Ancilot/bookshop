from django import forms
from shop.models import Product, Book, BoardGame, Stationery, Price


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


class BoardGameForm(forms.ModelForm):
    class Meta:
        model = BoardGame
        exclude = ['product']


class StationeryForm(forms.ModelForm):
    class Meta:
        model = Stationery
        exclude = ['product']