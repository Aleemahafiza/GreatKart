from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation, Coupon
from .models import Cart, CartItem, Wishlist
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse


# Create your views here.
from django.http import HttpResponse


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from .models import CartItem, Cart, Product


from django.shortcuts import get_object_or_404


def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)  # Get the product
    # If the user is authenticated
    if current_user.is_authenticated:
        product_variation = []
        if request.method == "POST":
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(
                        product=product,
                        variation_category__iexact=key,
                        variation_value__iexact=value,
                    )
                    product_variation.append(variation)
                except Variation.DoesNotExist:
                    pass

        # Get or create the user's cart
        cart, created = Cart.objects.get_or_create(user=current_user)

        # Check if the item already exists in the cart with the same variations
        matching_cart_items = CartItem.objects.filter(
            product=product, cart=cart, user=current_user
        )
        for cart_item in matching_cart_items:
            if list(cart_item.variations.all()) == product_variation:
                # If the item already exists with the same variations, increase the quantity
                cart_item.quantity += 1
                cart_item.save()
                print("Product quantity increased in cart:", product)
                return redirect("cart")

        # If no matching item found, create a new cart item and associate it with the cart
        cart_item = CartItem.objects.create(
            product=product, quantity=1, user=current_user, cart=cart
        )
        cart_item.variations.set(product_variation)
        cart_item.save()
        print("Product added to cart:", product)
        return redirect("cart")
    # If the user is not authenticated
    else:
        product_variation = []
        cart_id = _cart_id(request)
        cart, _ = Cart.objects.get_or_create(cart_id=cart_id)

        if request.method == "POST":
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(
                        product=product,
                        variation_category__iexact=key,
                        variation_value__iexact=value,
                    )
                    product_variation.append(variation)
                except:
                    pass

        try:
            cart_item = CartItem.objects.get(product=product, cart=cart)
            cart_item.quantity += 1
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                product=product, quantity=1, cart=cart
            )
            if product_variation:
                cart_item.variations.add(*product_variation)

        return redirect("cart")


def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)

    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(
                product=product, user=request.user, id=cart_item_id
            )
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(
                product=product, cart=cart, id=cart_item_id
            )

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except CartItem.DoesNotExist:
        pass

    return redirect("cart")


def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(
            product=product, user=request.user, id=cart_item_id
        )
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(
            product=product, cart=cart, id=cart_item_id
        )
    cart_item.delete()
    return redirect("cart")


from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Cart, CartItem

import logging

logger = logging.getLogger(__name__)


def cart(request):
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(
                user=request.user, is_active=True
            )
            cart_obj, created = Cart.objects.get_or_create(
                user=request.user
            )
            logger.info(f"Cart created: {created}")
            logger.info(f"Cart ID: {cart_obj.cart_id}")
            if request.method == "POST":
                coupon_code = request.POST.get("coupon")
                if coupon_code:
                    try:
                        coupon_obj = Coupon.objects.get(
                            coupon_code__iexact=coupon_code
                        )
                    except Coupon.DoesNotExist:
                        messages.warning(request, "Invalid Coupon")
                        return redirect("cart")

                    if cart_obj.coupon:
                        messages.error(
                            request, "Coupon already applied"
                        )
                        return redirect("cart")

                    grand_total, total, quantity, tax = (
                        cart_obj.calculate_grand_total()
                    )

                    if grand_total < coupon_obj.minimum_amount:
                        messages.warning(
                            request,
                            f"Minimum amount should be {coupon_obj.minimum_amount}",
                        )
                        return redirect("cart")

                    if coupon_obj.is_expired:
                        messages.warning(
                            request, "Coupon has been expired!"
                        )
                        return redirect("cart")

                    cart_obj.coupon = coupon_obj
                    cart_obj.save()
                    messages.success(request, "Coupon applied")

            grand_total, total, quantity, tax = (
                cart_obj.calculate_grand_total()
            )
        else:
            cart_obj = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(
                cart=cart_obj, is_active=True
            )
            grand_total, total, quantity, tax = (
                cart_obj.calculate_grand_total()
            )

        context = {
            "cart": cart_obj,
            "total": total,
            "quantity": quantity,
            "cart_items": cart_items,
            "tax": tax,
            "grand_total": grand_total,
        }
        return render(request, "store/cart.html", context)
    except ObjectDoesNotExist:
        return render(request, "store/cart.html")


def remove_coupon(request, id):
    cart = Cart.objects.get(pk=id)
    cart.coupon = None
    cart.save()
    messages.success(request, "Coupon removed")
    return redirect(
        request.META.get(
            "HTTP_REFERER", "redirect_if_referer_not_found"
        )
    )


from accounts.models import Address
from django.db import IntegrityError
from django.db.models import Max


@login_required(login_url="login")
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(
                user=request.user, is_active=True
            )
            is_address_exists = Address.objects.filter(
                user=request.user
            ).exists()
            request.session["referrer"] = "checkout"
            if is_address_exists:
                address = Address.objects.filter(user=request.user)
            else:
                return redirect(
                    "/orders/shipping_address?next=/carts/checkout"
                )
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(
                cart=cart, is_active=True
            )
        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grand_total = tax + total
    except ObjectDoesNotExist:
        pass
    context = {
        "total": total,
        "quantity": quantity,
        "cart_items": cart_items,
        "tax": tax,
        "grand_total": grand_total,
        "address": address,
    }
    return render(request, "store/checkout.html", context)
