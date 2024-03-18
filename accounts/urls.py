from django.urls import path
from . import views


urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    path(
        "login/forgotPassword/",
        views.forgotPassword,
        name="forgotPassword",
    ),
    path(
        "resetpassword_validate/<uidb64>/<token>/",
        views.resetpassword_validate,
        name="resetpassword_validate",
    ),
    path("resetPassword/", views.resetPassword, name="resetPassword"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("", views.dashboard, name="dashboard"),
    path("edit_profile/", views.edit_profile, name="edit_profile"),
    path("my_orders", views.my_orders, name="my_orders"),
    path("my_wallet", views.my_wallet, name="my_wallet"),
    path(
        "order_detail/<int:order_id>/",
        views.order_detail,
        name="order_detail",
    ),
    path(
        "cancel_order/<int:order_id>/",
        views.cancel_order,
        name="cancel_order",
    ),
    path(
        "request_refund/<int:order_id>/",
        views.request_refund,
        name="request_refund",
    ),
    path("my_address", views.my_address, name="my_address"),
    path(
        "edit_address/<int:id>/",
        views.edit_address,
        name="edit_address",
    ),
    path(
        "delete_address/<int:id>/",
        views.delete_address,
        name="delete_address",
    ),
    #  path('my-addresses/', views.my_addresses, name='my_addresses'),
    #  path('get-address-details/', views.get_address_details, name='get_address_details'),
    #  path('save-edited-address/', views.save_edited_address, name='save_edited_address'),
    #  path('delete-address/', views.delete_address, name='delete_address'),
]
