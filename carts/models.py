from urllib import request
from django.db import models
from store.models import Product, Variation
from accounts.models import Account
from store.models import Coupon
from decimal import Decimal
import uuid


class Cart(models.Model):
    user = models.ForeignKey(
        Account, on_delete=models.CASCADE, null=True, blank=True
    )
    cart_id = models.CharField(
        max_length=250, default=uuid.uuid4, unique=True
    )
    coupon = models.ForeignKey(
        Coupon, on_delete=models.SET_NULL, null=True, blank=True
    )
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id

    def calculate_grand_total(self):
        cart_items = CartItem.objects.filter(cart=self, is_active=True)
        print(f"Number of cart_items: {len(cart_items)}")
        total = Decimal("0.00")
        quantity = 0

        # Calculate total price and quantity
        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity
            quantity += cart_item.quantity
            print(
                f"CartItem: {cart_item.product.price} * {cart_item.quantity} = {cart_item.product.price * cart_item.quantity}"
            )

        # Calculate tax
        tax = (Decimal("2.00") * total) / Decimal("100.00")
        print(f"Tax: {tax}")

        # Apply coupon discount if available
        grand_total = total + tax
        if self.coupon:
            if grand_total > self.coupon.minimum_amount:
                grand_total -= min(
                    grand_total, self.coupon.discount_price
                )
                print(
                    f"Coupon Applied. Discount: {min(grand_total, self.coupon.discount_price)}"
                )

        print(
            f"Total: {total}, Quantity: {quantity}, Grand Total: {grand_total}"
        )
        return grand_total, total, quantity, tax


class CartItem(models.Model):
    user = models.ForeignKey(
        Account, on_delete=models.CASCADE, null=True
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        return self.product.price * self.quantity

    def __unicode__(self):
        return self.product


class Wishlist(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
