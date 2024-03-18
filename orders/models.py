from django.db import models
from accounts.models import Account
from store.models import Coupon, Product, Variation


class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(
        max_length=100
    )  # this is the total amount paid
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id


class OrderAddress(models.Model):
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email = models.EmailField()
    full_address = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.full_name}, {self.full_address}"


class Order(models.Model):
    STATUS = (
        ("New", "New"),
        ("Accepted", "Accepted"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
        ("Refunded", "Refunded"),
    )

    user = models.ForeignKey(
        Account, on_delete=models.SET_NULL, null=True
    )
    payment = models.ForeignKey(
        Payment, on_delete=models.SET_NULL, blank=True, null=True
    )
    address = models.ForeignKey(
        OrderAddress, on_delete=models.SET_NULL, blank=True, null=True
    )
    order_number = models.CharField(
        max_length=20, blank=True, null=True
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    order_note = models.CharField(max_length=100, blank=True)
    order_total = models.FloatField()
    tax = models.FloatField()
    status = models.CharField(
        max_length=10, choices=STATUS, default="New"
    )
    ip = models.CharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    coupon = models.ForeignKey(
        Coupon, on_delete=models.SET_NULL, null=True
    )
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def full_address(self):
        return f"{self.address_line_1} {self.address_line_2}"

    def __str__(self):
        return self.first_name


class OrderProduct(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, null=True
    )
    payment = models.ForeignKey(
        Payment, on_delete=models.SET_NULL, blank=True, null=True
    )
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.product_name


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"


# from django.db import models
# from django.contrib.auth.models import User

# class Notification(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,null=True)
#     message = models.CharField(max_length=255)
#     timestamp = models.DateTimeField(auto_now_add=True)
