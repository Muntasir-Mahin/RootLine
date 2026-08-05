from django.contrib.auth import views as auth_views
from django.urls import path

from . import views


urlpatterns = [
    path(
        "",
        views.home,
        name="home",
    ),

    path(
        "register/",
        views.register_view,
        name="register",
    ),

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html"
        ),
        name="login",
    ),

    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),

    path(
        "buyer/dashboard/",
        views.buyer_dashboard,
        name="buyer_dashboard",
    ),

    path(
        "seller/request/",
        views.seller_request,
        name="seller_request",
    ),

    path(
        "seller/dashboard/",
        views.seller_dashboard,
        name="seller_dashboard",
    ),

    path(
        "seller/products/add/",
        views.product_create,
        name="product_create",
    ),

    path(
        "products/<int:product_id>/",
        views.product_detail,
        name="product_detail",
    ),

    path(
        "products/<int:product_id>/bid/",
        views.place_bid,
        name="place_bid",
    ),

    path(
        "products/<int:product_id>/buy/",
        views.buy_now,
        name="buy_now",
    ),
]