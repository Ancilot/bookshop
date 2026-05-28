from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


app_name = 'account'

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('edit/', views.edit, name='edit'),
    path('verify-email/', views.verify_email, name='verify_email'),
    path(
        'password-change/',
        views.CustomPasswordChangeView.as_view(),
        name='password_change'
    ),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='account/password_change_done.html'
    ), name='password_change_done'),
    path('password-change-request/', views.password_change_request, name='password_change_request'),
    path('password-change-confirm/', views.password_change_confirm, name='password_change_confirm'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-confirm/', views.reset_confirm, name='reset_confirm'),
    path('set-new-password/', views.set_new_password, name='set_new_password'),
    path('confirm-email-change/', views.confirm_email_change, name='confirm_email_change'),
    path('change-email/', views.change_email, name='change_email'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='wishlist_toggle'),
    path('wishlist/', views.wishlist, name='wishlist_list'),

]