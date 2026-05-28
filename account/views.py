from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserEditForm, BuyerProfileForm
from .models import Buyer

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import EmailChangeForm
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth.models import User
from .utils import generate_code, send_registration_code, send_password_reset_code, send_email_change_code
from django.core.mail import send_mail
from django.conf import settings

from django.contrib.auth.views import PasswordChangeView

from django.contrib.auth import update_session_auth_hash
from .forms import PasswordChangeRequestForm, CodeForm

from time import time


@login_required
def password_change_request(request):
    error = None

    if request.method == 'POST':
        form = PasswordChangeRequestForm(request.POST)

        if form.is_valid():
            user = request.user

            # проверка старого пароля
            if not user.check_password(form.cleaned_data['old_password']):
                error = "Неверный старый пароль"
            else:
                code = generate_code()

                request.session['password_change'] = {
                    'user_id': user.id,
                    'new_password': form.cleaned_data['new_password'],
                    'code': code,
                    'created_at': time()
                }

                send_password_reset_code(user.email, code)

                return redirect('account:password_change_confirm')
    else:
        form = PasswordChangeRequestForm()

    return render(request, 'account/password_change_request.html', {
        'form': form,
        'error': error
    })

@login_required
def password_change_confirm(request):
    data = request.session.get('password_change')
    if not data:
        return redirect('account:password_change_request')
    if time() - data['created_at'] > 300:
        del request.session['password_change']
        return redirect('account:password_change_request')

    if not data:
        return redirect('account:password_change_request')

    error = None

    if request.method == 'POST':
        form = CodeForm(request.POST)

        if form.is_valid():

            if form.cleaned_data['code'] == data['code']:

                user = User.objects.get(id=data['user_id'])
                user.set_password(data['new_password'])
                user.save()

                # важно сохранить сессию (иначе разлогинит)
                update_session_auth_hash(request, user)

                del request.session['password_change']

                return redirect('account:dashboard')

            else:
                error = "Неверный код"
    else:
        form = CodeForm()

    return render(request, 'account/password_change_confirm.html', {
        'form': form,
        'error': error
    })

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'account/password_change.html'
    success_url = '/account/password-change/done/'

    def form_valid(self, form):
        response = super().form_valid(form)

        send_mail(
            "Пароль изменён",
            "Ваш пароль был успешно изменён.",
            settings.DEFAULT_FROM_EMAIL,
            [self.request.user.email],
        )

        return response

def reset_confirm(request):
    data = request.session.get('reset_password')
    if not data:
        return redirect('account:forgot_password')
    if time() - data['created_at'] > 300:
        del request.session['reset_password']
        return redirect('account:forgot_password')

    if not data:
        return redirect('account:forgot_password')

    error = None
    form = CodeForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():

            if form.cleaned_data['code'] == data['code']:
                request.session['reset_verified'] = True
                return redirect('account:set_new_password')

            error = "Неверный код"

    return render(request, 'account/password_change_confirm.html', {
        'form': form,
        'error': error
    })

def set_new_password(request):
    data = request.session.get('reset_password')

    if not data or not request.session.get('reset_verified'):
        return redirect('account:forgot_password')

    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            return render(request, 'account/set_new_password.html', {
                'error': 'Пароли не совпадают'
            })

        user = User.objects.get(id=data['user_id'])
        user.set_password(password1)
        user.save()

        request.session.pop('reset_password', None)
        request.session.pop('reset_verified', None)

        return redirect('account:login')

    return render(request, 'account/set_new_password.html')

def forgot_password(request):
    error = None

    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)

            code = generate_code()

            request.session['reset_password'] = {
                'user_id': user.id,
                'code': code,
                'created_at': time()
            }

            send_password_reset_code(email, code)

            return redirect('account:reset_confirm')

        except User.DoesNotExist:
            error = "Пользователь не найден"

    return render(request, 'account/forgot_password.html', {
        'error': error
    })

def verify_email(request):
    session_data = request.session.get('reg_data')
    if not session_data:
        return redirect('account:register')

    if time() - session_data['created_at'] > 300:
        del request.session['reg_data']
        return redirect('account:register')

    if not session_data:
        return redirect('account:register')

    form = CodeForm(request.POST or None)
    error = None

    if request.method == 'POST':
        if form.is_valid():

            if form.cleaned_data['code'] == session_data['code']:

                user = User.objects.create(
                    username=session_data['username'],
                    email=session_data['email'],
                    first_name=session_data['first_name'],
                )
                user.set_password(session_data['password'])
                user.save()

                Buyer.objects.create(user=user)

                request.session.pop('reg_data', None)

                return redirect('account:login')

            error = "Неверный код"

    return render(request, 'account/verify_email.html', {
        'form': form,
        'error': error
    })


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

            if user.is_superuser:
                return redirect('admin_panel:dashboard')

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

            code = generate_code()

            request.session['reg_data'] = {
                'username': form.cleaned_data['username'],
                'email': form.cleaned_data['email'],
                'first_name': form.cleaned_data['first_name'],
                'password': form.cleaned_data['password'],
                'code': code,
                'created_at': time()
            }

            send_registration_code(form.cleaned_data['email'], code)

            return redirect('account:verify_email')

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
        fields = ['first_name', 'last_name']

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')

        if not first_name:
            raise forms.ValidationError("Имя обязательно")

        return first_name




@login_required
def edit(request):
    buyer, created = Buyer.objects.get_or_create(user=request.user)

    success = None

    if request.method == 'POST':

        user_form = UserEditForm(
            request.POST,
            instance=request.user
        )

        buyer_form = BuyerProfileForm(
            request.POST,
            request.FILES,
            instance=buyer
        )

        if user_form.is_valid() and buyer_form.is_valid():

            user_form.save()
            buyer_form.save()

            success = "Профиль обновлён"

    else:
        user_form = UserEditForm(instance=request.user)
        buyer_form = BuyerProfileForm(instance=buyer)

    return render(request, 'account/edit.html', {
        'user_form': user_form,
        'buyer_form': buyer_form,
        'success': success,
    })

@login_required
def confirm_email_change(request):
    data = request.session.get('email_change')
    if not data:
        return redirect('account:change_email')
    if time() - data['created_at'] > 300:
        del request.session['email_change']
        return redirect('account:change_email')

    form = CodeForm(request.POST or None)
    error = None

    if request.method == 'POST':
        if form.is_valid():

            if form.cleaned_data['code'] == data['code']:

                user = User.objects.get(id=data['user_id'])
                user.email = data['new_email']
                user.save()

                del request.session['email_change']

                return redirect('account:edit')

            error = "Неверный код"

    return render(request, 'account/confirm_email_change.html', {
        'form': form,
        'error': error
    })

@login_required
def change_email(request):

    error = None

    if request.method == 'POST':

        form = EmailChangeForm(request.user, request.POST)

        if form.is_valid():

            new_email = form.cleaned_data['new_email']

            code = generate_code()

            request.session['email_change'] = {
                'user_id': request.user.id,
                'new_email': new_email,
                'code': code,
                'created_at': time()
            }


            send_email_change_code(new_email, code)

            return redirect('account:confirm_email_change')

    else:
        form = EmailChangeForm(request.user)

    return render(request, 'account/change_email.html', {
        'form': form,
        'error': error
    })