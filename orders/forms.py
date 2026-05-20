from django import forms
from account.models import Address


class OrderCreateForm(forms.ModelForm):

    class Meta:
        model = Address

        fields = [
            'country',
            'region',
            'city',
            'street',
            'house',
        ]

        widgets = {
            'country': forms.TextInput(attrs={'class': 'form-input'}),
            'region': forms.TextInput(attrs={'class': 'form-input'}),
            'city': forms.TextInput(attrs={'class': 'form-input'}),
            'street': forms.TextInput(attrs={'class': 'form-input'}),
            'house': forms.TextInput(attrs={'class': 'form-input'}),
        }