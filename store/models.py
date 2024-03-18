from email.policy import default
from itertools import count
import uuid
from django.db import models
from accounts.models import Account
from category.models import Category
from django.urls import reverse
from django.db.models import Avg, Count, Sum


class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=200, blank=True)
    price = models.IntegerField()
    image = models.ImageField(upload_to="photos/products")
    stock = models.IntegerField(default=0)
    is_active = models.IntegerField(default=1)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse(
            "product_detail", args=[self.category.slug, self.slug]
        )

    def get_absolute_url(self):
        return reverse("product_list")

    def __str__(self):
        return self.product_name

    def averageReview(self):
        reviews = ReviewRating.objects.filter(
            product=self, status=True
        ).aggregate(average=Avg("rating"))
        avg = 0
        if reviews["average"] is not None:
            avg = float(reviews["average"])
        return avg

    def countReview(self):
        reviews = ReviewRating.objects.filter(
            product=self, status=True
        ).aggregate(count=Count("id"))
        count = 0
        if reviews["count"] is not None:
            count = int(reviews["count"])
        return count

    def total_stock(self):
        variations = Variation.objects.filter(product=self)
        total_stock = variations.aggregate(Sum("stock"))["stock__sum"]
        return total_stock if total_stock is not None else 0


class VariationManager(models.Manager):

    def colors(self):
        return super(VariationManager, self).filter(
            variation_category="color", is_active=True
        )

    def sizes(self):
        return super(VariationManager, self).filter(
            variation_category="size", is_active=True
        )


variation_category_choices = (("color", "color"), ("size", "size"))


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(
        max_length=100, choices=variation_category_choices, null=True
    )
    variation_value = models.CharField(max_length=100, null=True)
    is_active = models.BooleanField(default=True)
    created_date = models.DateField(auto_now=True)
    quantity = models.IntegerField(default=0)

    objects = VariationManager()

    def get_absolute_url(self):
        return reverse("variation")

    def __str__(self):
        return self.variation_value


class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=100, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject


class ProductGallery(models.Model):
    product = models.ForeignKey(
        Product, default=None, on_delete=models.CASCADE
    )
    image = models.ImageField(
        upload_to="store/products", max_length=255
    )

    def __str__(self):
        return self.product.product_name


class Coupon(models.Model):
    uid = models.UUIDField(
        primary_key=True, editable=False, default=uuid.uuid4
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    coupon_code = models.CharField(max_length=10)
    is_expired = models.BooleanField(default=False)
    discount_price = models.IntegerField(default=100)
    minimum_amount = models.IntegerField(default=500)

    def __str__(self):
        return self.coupon_code

    def reset_availability(self):
        self.is_expired = False
        self.save()
