
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserEditForm, BuyerProfileForm
from .models import Buyer

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth.models import User


def user_logout(request):
    logout(request)
    return redirect('account:login')

def user_login(request):
    error = None

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            return redirect('account:dashboard')

        else:
            error = 'Неверный логин или пароль'

    else:
        form = AuthenticationForm()

    return render(request, 'account/login.html', {
        'form': form,
        'error': error,
    })

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Создаем пользователя
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()

            # Создаем профиль покупателя
            Buyer.objects.create(
                user=new_user
            )

            messages.success(request, 'Регистрация успешна! Теперь вы можете войти.')
            return redirect('account:login')
    else:
        form = UserRegistrationForm()

    return render(request, 'account/register.html', {'form': form})


@login_required
def dashboard(request):
    # Получаем корзину пользователя
    cart_items = request.user.buyer.cart_items.all() if hasattr(request.user, 'buyer') else []
    total_cart_items = sum(item.quantity for item in cart_items)

    # Получаем избранное
    wishlist_items = request.user.buyer.wishlist.all() if hasattr(request.user, 'buyer') else []

    return render(request, 'account/dashboard.html', {
        'section': 'dashboard',
        'cart_items': cart_items,
        'total_cart_items': total_cart_items,
        'wishlist_items': wishlist_items,
    })

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')

        if not first_name:
            raise forms.ValidationError("Имя обязательно")

        return first_name

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if not email:
            raise forms.ValidationError("Email обязателен")

        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError("Этот email уже используется")

        return email

@login_required
def edit(request):
    buyer, created = Buyer.objects.get_or_create(user=request.user)

    success = None

    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        buyer_form = BuyerProfileForm(
            instance=buyer,
            data=request.POST,
            files=request.FILES
        )

        if user_form.is_valid() and buyer_form.is_valid():
            user_form.save()
            buyer_form.save()
            success = "Профиль успешно обновлен"
    else:
        user_form = UserEditForm(instance=request.user)
        buyer_form = BuyerProfileForm(instance=buyer)

    return render(request, 'account/edit.html', {
        'user_form': user_form,
        'buyer_form': buyer_form,
        'success': success,
    })