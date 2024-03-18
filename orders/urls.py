from django.urls import path
from . import views

urlpatterns = [
    path(
        "shipping_address",
        views.shipping_address,
        name="shipping_address",
    ),
    path("place_order/", views.place_order, name="place_order"),
    path("payments/", views.payments, name="payments"),
    path(
        "order_complete/", views.order_complete, name="order_complete"
    ),
    path("cod/<int:order_number>/", views.cod, name="cod"),
    path(
        "cod_order_complete/<int:order_number>/",
        views.cod_order_complete,
        name="cod_order_complete",
    ),
    path(
        "download_invoice/<str:order_number>/",
        views.download_invoice_paypal,
        name="download_invoice",
    ),
    path(
        "download_invoice_cod/<str:order_number>/",
        views.download_invoice_cod,
        name="download_invoice_cod",
    ),
]
