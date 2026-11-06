from django.urls import path

from .views import (
    RegisterView,
    LoginView,
    ProfileView,
    LogoutView
)

urlpatterns = [
    # Routes existantes
    path("register/", RegisterView.as_view()),
    path("login/", LoginView.as_view()),
    path("me/", ProfileView.as_view()),
    path("logout/", LogoutView.as_view()),

    # Routes sans slash final pour React
    path("register", RegisterView.as_view()),
    path("login", LoginView.as_view()),
    path("me", ProfileView.as_view()),
    path("logout", LogoutView.as_view()),
]