from multiprocessing import context
from django.shortcuts import get_object_or_404, render, redirect
from accounts.forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account, UserProfile
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from orders.models import Refund
from orders.forms import RefundForm, AddressForm

# from orders.models import Address
# VARIFICATION EMAIL
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import (
    urlsafe_base64_encode,
    urlsafe_base64_decode,
)
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from carts.models import Cart, CartItem
from carts.views import _cart_id
from orders.models import Order, OrderProduct
import requests
from decimal import Decimal

# Create your views here.


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            phone_number = form.cleaned_data["phone_number"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            username = email.split("@")[0]
            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
            )
            user.phone_number = phone_number
            user.save()

            # USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = "Please Activate Your Account"
            message = render_to_string(
                "accounts/accout_varification_email.html",
                {
                    "user": user,
                    "domain": current_site,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user),
                },
            )
            to_email = email
            # sender = 'aleemahafiza98@gmail.com'
            send_email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            send_email.send()
            # messages.success(request,'Thank You for registering with us we have sent a verification email to your email address please verify it.')
            return redirect(
                "/accounts/login/?command=verification&email=" + email
            )
    else:
        form = RegistrationForm()
    context = {
        "form": form,
    }
    return render(request, "accounts/register.html", context)


from django.contrib import auth, messages
from django.shortcuts import render, redirect


def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(
                    cart=cart
                ).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    # getting the product variation by cart id
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    # GET THE CART ITEM FROM THE USER TO ACCESS HIS PRODUCT VARIATIONS
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(
                                cart=cart
                            )
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass
            auth.login(request, user)
            messages.success(request, "You Are Now Logged In.")
            url = request.META.get("HTTP_REFERER")
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split("=") for x in query.split("&"))
                if "next" in params:
                    nextpage = params["next"]
                    return redirect(nextpage)
            except:
                return redirect("dashboard")
        else:
            messages.error(request, "Invalid Login Credentials")
            return redirect("login")

    return render(request, "accounts/login.html")


@login_required(login_url="login")
def logout(request):
    auth.logout(request)
    messages.success(request, "You are logged out")
    return redirect("login")


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(
        user, token
    ):
        user.is_active = True
        user.save()
        messages.success(
            request, "Congratulations! Your account is activated"
        )
        return redirect("login")
    else:
        messages.error(request, "Invalid activation link.")
        return redirect("register")


def forgotPassword(request):
    if request.method == "POST":
        email = request.POST["email"]
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__iexact=email)
            current_site = get_current_site(request)
            mail_subject = "Reset Your Password"
            message = render_to_string(
                "accounts/reset_password_email.html",
                {
                    "user": user,
                    "domail": current_site,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user),
                },
            )
            to_email = email
            # sender = 'aleemahafiza98@gmail.com'
            send_email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            send_email.send()

            messages.success(
                request,
                "Password reset email has been sent to your email address.",
            )
            return redirect("login")

        else:
            messages.error(request, "Account does not exist")
            return redirect("forgotPassword")
    return render(request, "accounts/forgotPassword.html")


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(
        user, token
    ):
        request.session["uid"] = uid
        messages.success(request, "Please reset your password")
        return redirect("resetPassword")
    else:
        messages.error(request, "This link has been expired")
        return redirect("login")


def resetPassword(request):
    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password == confirm_password:
            uid = request.session.get("uid")
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, "Password reset successful")
            return redirect("login")
        else:
            messages.error(request, "Password do not match")
            return redirect("resetPassword")
    else:
        return render(request, "accounts/resetPassword.html")


from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserForm, UserProfileForm
from .models import UserProfile
from django.contrib.auth.decorators import login_required


@login_required(login_url="login")
def dashboard(request):
    orders = Order.objects.order_by("-created_at").filter(
        user_id=request.user.id, is_ordered=True
    )
    orders_count = orders.count()
    context = {"orders_count": orders_count}
    return render(request, "accounts/dashboard.html", context)


from django.shortcuts import get_object_or_404


@login_required(login_url="login")
def edit_profile(request):
    userprofile, created = UserProfile.objects.get_or_create(
        user=request.user
    )
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST, request.FILES, instance=userprofile
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("edit_profile")
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        "user_form": user_form,
        "profile_form": profile_form,
        "userprofile": userprofile,
    }
    return render(request, "accounts/edit_profile.html", context)


@login_required(login_url="login")
def my_wallet(request):
    account = Account.objects.get(email=request.user)
    context = {"account": account}
    return render(request, "accounts/my_wallet.html", context)


def my_orders(request):
    orders = Order.objects.filter(
        user=request.user, is_ordered=True
    ).order_by("-created_at")
    context = {"orders": orders}
    return render(request, "accounts/my_orders.html", context)


@login_required(login_url="login")
def order_detail(request, order_id):
    current_user = request.user
    cart = Cart.objects.get(user=current_user)
    order_detail = OrderProduct.objects.filter(
        order__order_number=order_id
    )
    order = Order.objects.get(order_number=order_id)
    sub_total = 0
    for i in order_detail:
        sub_total += i.product_price * i.quantity

    for item in order_detail:
        item.total_price = item.product_price * item.quantity

    context = {
        "cart": cart,
        "total_price": item.total_price,
        "order_detail": order_detail,
        "order": order,
        "sub_total": sub_total,
    }
    return render(request, "accounts/order_detail.html", context)


from django.shortcuts import get_object_or_404
from django.contrib import messages
from decimal import Decimal


def cancel_order(request, order_id):
    order = get_object_or_404(Order, order_number=order_id)
    if order.status:
        order.status = "Cancelled"
        if order.payment and order.payment.payment_method != "cod":
            wallet = Decimal(str(order.order_total))
            user = order.user
            user.wallet += wallet
            user.save()
        order.save()
        messages.success(request, "Order Cancelled Successfully.")
    else:
        messages.error(request, "Failed to cancel order.")
    return redirect(
        "order_detail", order_id=order_id
    )  # Assuming you have a view named 'order_detail' for displaying order details


def request_refund(request, order_id):
    account = Account.objects.get(email=request.user)
    order = Order.objects.get(order_number=order_id)
    if request.method == "POST":
        form = RefundForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data["reason"]
            email = form.cleaned_data["email"]
            try:
                order.refund_requested = True
                order.status = "hold"
                order.save()
                refund = Refund()
                refund.order = order
                refund.reason = reason
                refund.email = email
                refund.save()
                messages.info(request, "Your request was received.")
                return redirect("my_orders")
            except Order.DoesNotExist:
                messages.error(request, "This order does not exist")
                return redirect("my_orders")
    else:
        # Initialize the form without passing order_number
        form = RefundForm(
            initial={
                "email": account.email,
                "order_number": order.order_number,
            }
        )

    context = {"form": form, "order": order}
    return render(request, "accounts/request_refund.html", context)


from django.db.models import Max

# views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Address


@login_required(login_url="login")
def my_address(request):
    addresses = Address.objects.filter(user=request.user)
    context = {"addresses": addresses}
    return render(request, "accounts/my_address.html", context)


def edit_address(request, id):
    address = Address.objects.get(pk=id)
    address_form = AddressForm(instance=address)
    context = {
        "address_form": address_form,
        "address": address,
    }
    if request.method == "POST":
        address.first_name = request.POST["first_name"]
        address.last_name = request.POST["last_name"]
        address.email = request.POST["email"]
        address.phone = request.POST["phone"]
        address.address_line_1 = request.POST["address_line_1"]
        address.address_line_2 = request.POST["address_line_2"]
        address.state = request.POST["state"]
        address.city = request.POST["city"]
        address.country = request.POST["country"]
        address.save()
        messages.success(request, "Your address has been updated")
        return redirect("my_address")
    return render(request, "accounts/edit_address.html", context)


@login_required(login_url="login")
def delete_address(request, id):
    address = Address.objects.get(id=id)
    address.delete()
    return redirect("my_address")


# def my_addresses(request):
#     unique_saved_addresses = (
#         Address.objects
#         .filter(user=request.user, is_saved_address=True)
#         .values('address_line_1', 'city', 'state', 'country')
#         .annotate(max_id=Max('id'))
#     )

#     saved_addresses = Address.objects.filter(id__in=unique_saved_addresses.values('max_id'))

#     context = {
#         'saved_addresses': saved_addresses,
#     }
#     return render(request, "accounts/my_address.html", context)

# def get_address_details(request):
#     if request.method == 'GET':
#         address_id = request.GET.get('address_id')
#         address = get_object_or_404(Address, id=address_id)

#         data = {
#             'first_name': address.first_name,
#             'last_name': address.last_name,
#             'phone': address.phone,
#             'email': address.email,
#             'address_line_1': address.address_line_1,
#             'address_line_2': address.address_line_2,
#             'country': address.country,
#             'state': address.state,
#             'city': address.city,
#             'pincode': address.pincode,
#             'order_note': address.order_note,
#         }
#         return JsonResponse(data)
#     else:
#         return JsonResponse({'error': 'Invalid request method'})

# @require_POST
# def save_edited_address(request):
#     if request.method == 'POST':
#         address_id = request.POST.get('address_id')
#         address = get_object_or_404(Address, id=address_id)

#         address_fields = [
#             'first_name', 'last_name', 'phone', 'email',
#             'address_line_1', 'address_line_2', 'country',
#             'state', 'city', 'pincode', 'order_note'
#         ]

#         # Update address fields with the edited data
#         for field in address_fields:
#             new_value = request.POST.get(field)
#             if new_value is not None:
#                 setattr(address, field, new_value)

#         # Save the updated address
#         address.save()

#         return JsonResponse({'success': True})
#     else:
#         return JsonResponse({'error': 'Invalid request method'})

# @require_POST
# def delete_address(request):
#     address_id = request.POST.get('address_id')
#     address = get_object_or_404(Address, id=address_id)
#     address.delete()
#     return JsonResponse({'message': 'Address deleted successfully'})
