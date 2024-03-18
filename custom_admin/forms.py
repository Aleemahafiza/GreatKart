from django.forms import ModelForm
from django import forms
from orders.models import Order


class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = ["user", "order_number", "order_total", "status"]

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        readonly_fields = ["user", "order_number", "order_total"]

        for field_name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-control col-8"})
