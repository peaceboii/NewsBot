from django.urls import path
from . import views
urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("fetch_and_store/", views.fetch_and_store, name="fetch_and_store"),
    path("logout/", views.logout_view, name="logout"),

]