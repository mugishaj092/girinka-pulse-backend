from django.urls import path
from .views import (
    LoginView, LogoutView, TokenRefreshView,
    PasswordResetRequestView, PasswordResetConfirmView,
    PasswordChangeView, MeView,
)

urlpatterns = [
    path("login/",            LoginView.as_view()),
    path("logout/",           LogoutView.as_view()),
    path("token/refresh/",    TokenRefreshView.as_view()),
    path("password/reset/",   PasswordResetRequestView.as_view()),
    path("password/confirm/", PasswordResetConfirmView.as_view()),
    path("password/change/",  PasswordChangeView.as_view()),
    path("me/",               MeView.as_view()),
]
