from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from store.models import Coupon
from orders.models import Refund
from django.contrib import auth, messages
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DetailView,
    View,
)
from category.models import Category
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from accounts.models import UserProfile
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DetailView,
    View,
)
from django.shortcuts import render
from store.models import Variation
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from accounts.models import *
from accounts.models import Account
from django.db.models import Sum
from orders.models import Order, OrderProduct
from decimal import Decimal
from django.views.decorators.cache import never_cache
from .forms import OrderForm
from django.contrib.auth.mixins import LoginRequiredMixin
from carts.models import Cart
from django.db.models import Sum, Count
from django.db.models.functions import (
    ExtractWeek,
    ExtractMonth,
    ExtractYear,
    ExtractDay,
)
import json


def user_is_admin(user):
    return user.is_staff


def adminlogin(request):
    if request.method == "POST":
        adminemail = request.POST["adminemail"]
        adminpassword = request.POST["adminpassword"]

        user = auth.authenticate(
            email=adminemail, password=adminpassword
        )

        if user is not None and user.is_superadmin:
            auth.login(request, user)
            messages.success(request, "You Are Now Logged In.")
            return redirect("admin_dashboard")

        elif user is not None and not user.is_superadmin:
            # User exists but is not a superuser
            messages.error(request, "You are not a superuser")
            return redirect(
                "adminlogin"
            )  # Redirect to login to display the error message

        else:
            messages.error(request, "Invalid Login Credentials")
            return redirect("adminlogin")

    return render(request, "admin/adminpages/login.html")


@user_passes_test(user_is_admin, login_url="/customadmin/adminlogin")
@login_required(login_url="/customadmin/adminlogin")
@never_cache
def adminhome(request):
    return render(request, "admin/adminpages/index.html")


def adminlogout(request):
    logout(request)
    messages.success(request, "Logout Successfull!")
    return HttpResponseRedirect(reverse("adminlogin"))


# <<--------------------USER PROFILE  -------->>


# <<--------------------ADMIN USER MANAGEMENT -------->>
@method_decorator(
    user_passes_test(
        user_is_admin, login_url="/customadmin/adminlogin"
    ),
    name="dispatch",
)
@method_decorator(never_cache, name="dispatch")
class UserProfileList(LoginRequiredMixin, ListView):
    model = UserProfile
    template_name = "admin/adminpages/userprofile_list.html"
    paginate_by = 2

    def get_queryset(self):
        filter_val = self.request.GET.get("filter", "")
        order_by = self.request.GET.get("orderby", "id") or "id"

        if filter_val != "":
            user = UserProfile.objects.filter(
                Q(user__first_name__icontains=filter_val)
                | Q(user__last_name__icontains=filter_val)
            ).order_by(order_by)
        else:
            user = UserProfile.objects.all().order_by(order_by)
        return user

    def get_context_data(self, **kwargs):
        context = super(UserProfileList, self).get_context_data(
            **kwargs
        )
        context["filter"] = self.request.GET.get("filter", "")
        context["orderby"] = self.request.GET.get("orderby", "")
        context["all_table_fields"] = UserProfile._meta.get_fields()
        return context


@method_decorator(
    user_passes_test(
        user_is_admin, login_url="/customadmin/adminlogin"
    ),
    name="dispatch",
)
@method_decorator(never_cache, name="dispatch")
class UserDetail(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = "admin/adminpages/userdetail.html"
    context_object_name = "user_profile"

    def user_detail_view(request, user_profile_id):
        user_profile = UserProfile.objects.get(pk=user_profile_id)
        return render(
            request,
            "admin/adminpages/userdetail.html",
            {"user_profile": user_profile},
        )


# <<--------------------VARIATIONS -------------------------->>


@method_decorator(
    user_passes_test(
        user_is_admin, login_url="/customadmin/adminlogin"
    ),
    name="dispatch",
)
@method_decorator(never_cache, name="dispatch")
class VariationList(LoginRequiredMixin, ListView):
    model = Variation
    template_name = "admin/adminpages/variation.html"
    context_object_name = "variations"
    paginate_by = 10

    def get_queryset(self):
        filter_val = self.request.GET.get("filter", "")
        order_by = self.request.GET.get("orderby", "id") or "id"

        if filter_val != "":
            variation = Variation.objects.filter(
                Q(variation__product__icontains=filter_val)
                | Q(variation__variation_value__icontains=filter_val)
            ).order_by(order_by)
        else:
            variation = Variation.objects.all().order_by(order_by)
        return variation

    def get_context_data(self, **kwargs):
        context = super(VariationList, self).get_context_data(**kwargs)
        context["filter"] = self.request.GET.get("filter", "")
        context["orderby"] = self.request.GET.get("orderby", "")
        context["all_table_fields"] = Variation._meta.get_fields()
        return context


@method_decorator(
    user_passes_test(
        user_is_admin, login_url="/customadmin/adminlogin"
    ),
    name="dispatch",
)
@method_decorator(never_cache, name="dispatch")
class VariationCreate(
    LoginRequiredMixin, SuccessMessageMixin, CreateView
):
    model = Variation
    success_message = "Variation Successfully Added!"
    fields = "__all__"
    template_name = "admin/adminpages/variation_create.html"


# <<--------------------ADMIN CATEGORY ADDITION -------->>

from django.db.models import Sum
from django.db.models import Count

from django.db.models import Count


class CategoriesListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = "admin/adminpages/category_list.html"
    paginate_by = 4

    def get_queryset(self):
        filter_val = self.request.GET.get("filter", "")
        order_by = self.request.GET.get("orderby", "id") or "id"

        if filter_val:
            queryset = Category.objects.filter(
                Q(category_name__icontains=filter_val)
                | Q(description__icontains=filter_val)
            ).order_by(order_by)
        else:
            queryset = Category.objects.all().order_by(order_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = self.request.GET.get("filter", "")
        context["orderby"] = self.request.GET.get("orderby", "")
        context["all_table_fields"] = Category._meta.get_fields()

        # Retrieve top 10 best-selling categories
        top_categories = Category.objects.annotate(
            total_orders=Count("product__orderproduct")
        ).order_by("-total_orders")[:10]

        context["top_categories"] = top_categories
        return context


from django.db.models import Count

from django.db.models import Count
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from category.models import Category
from django.db.models import Sum


class BestSellingCategories(LoginRequiredMixin, ListView):
    model = Category
    template_name = "admin/adminpages/best_selling_category.html"
    paginate_by = 10

    def get_queryset(self):
        # Get the top 10 best-selling categories based on total quantity sold
        top_categories = Category.objects.annotate(
            total_quantity_sold=Sum("product__orderproduct__quantity")
        ).order_by("-total_quantity_sold")[:10]

        return top_categories

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        top_categories = self.get_queryset()
        context["top_categories"] = [
            (category, category.total_quantity_sold)
            for category in top_categories
        ]
        return context


@method_decorator(
    user_passes_test(
        user_is_admin, login_url="/customadmin/adminlogin"
    ),
    name="dispatch",
)
@method_decorator(never_cache, name="dispatch")
class CategoriesCreate(
    LoginRequiredMixin, SuccessMessageMixin, CreateView
):
    model = Category
    success_message = "Category Successfully Added!"
    fields = "__all__"
    template_name = "admin/adminpages/category_create.html"


@method_decorator(
    user_passes_test(
        user_is_admin, login_url="/customadmin/adminlogin"
    ),
    name="dispatch",
)
@method_decorator(never_cache, name="dispatch")
class CategoriesUpdate(
    LoginRequiredMixin, SuccessMessageMixin, UpdateView
):
    model = Category
    success_message = "Category Successfully Update!"
    fields = "__all__"
    template_name = "admin/adminpages/category_update.html"


# <<--------------------ADMIN PRODUCT ADDITION -------->>
from store.models import Product


@method_decorator(
    user_passes_test(
        user_is_admin, login_url="/customadmin/adminlogin"
    ),
    name="dispatch",
)
@method_decorator(never_cache, name="dispatch")
class ProductCreateView(
    LoginRequiredMixin, SuccessMessageMixin, CreateView
):
    model = Product
    fields = [
        "product_name",
        "slug",
        "description",
        "price",
        "image",
        "stock",
        "category",
    ]
    success_message = "Product Successfully Added!"
    template_name = "admin/adminpages/product_create.html"

    def get(self, request, *args, **kwargs):
        categories = Category.objects.filter(is_active=1)
        categories_list = []
        for category in categories:
            categories_list.append({"category": category})
        return render(
            request,
            "admin/adminpages/product_create.html",
            {"categories": categories_list},
        )


from django.db.models import Count


class ProductsListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = "admin/adminpages/product_list.html"
    paginate_by = 4

    def get_queryset(self):
        filter_val = self.request.GET.get("filter", "")
        order_by = self.request.GET.get("orderby", "id") or "id"

        if filter_val:
            queryset = Product.objects.filter(
                Q(product_name__icontains=filter_val)
                | Q(description__icontains=filter_val)
            ).order_by(order_by)
        else:
            queryset = Product.objects.all().order_by(order_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = self.request.GET.get("filter", "")
        context["orderby"] = self.request.GET.get("orderby", "")
        context["all_table_fields"] = Product._meta.get_fields()

        # Get top 10 best-selling products
        top_products = Product.objects.annotate(
            total_orders=Count("orderproduct")
        ).order_by("-total_orders")[:10]

        context["top_products"] = top_products
        return context

    from django.db.models import Count


class BestSellingProduct(LoginRequiredMixin, ListView):
    model = Product
    template_name = "admin/adminpages/best_selling_product.html"
    paginate_by = 4

    def get_queryset(self):
        filter_val = self.request.GET.get("filter", "")
        order_by = self.request.GET.get("orderby", "id") or "id"

        if filter_val:
            queryset = Product.objects.filter(
                Q(product_name__icontains=filter_val)
                | Q(description__icontains=filter_val)
            ).order_by(order_by)
        else:
            queryset = Product.objects.all().order_by(order_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = self.request.GET.get("filter", "")
        context["orderby"] = self.request.GET.get("orderby", "")
        context["all_table_fields"] = Product._meta.get_fields()

        # Get top 10 best-selling products
        top_products = Product.objects.annotate(
            total_orders=Count("orderproduct")
        ).order_by("-total_orders")[:10]

        context["top_products"] = top_products
        return context


@method_decorator(
    user_passes_test(
        user_is_admin, login_url="/customadmin/adminlogin"
    ),
    name="dispatch",
)
@method_decorator(never_cache, name="dispatch")
class ProductUpdate(SuccessMessageMixin, UpdateView):
    model = Product
    success_message = "Product Successfully Update!"
    fields = "__all__"
    template_name = "admin/adminpages/product_update.html"


# -------------------------------------------

from django.shortcuts import redirect


def deletecategory(request, pk):
    instance = Category.objects.get(pk=pk)
    instance.delete()
    return redirect("category_list")


def deleteproduct(request, pk):
    instance = Product.objects.get(pk=pk)
    instance.delete()
    return redirect("product_list")


# <<--------------------ADMIN DASHBOARD ADDITION -------->>


@user_passes_test(user_is_admin, login_url="/customadmin/adminlogin")
@login_required(login_url="/customadmin/adminlogin")
@never_cache
def admin_dashboard(request):
    products = Product.objects.all()
    total_stock = 0
    for product in products:
        stock = product.stock
        print("stock", products, stock)
        total_stock += stock
        print(total_stock)
    users = Account.objects.filter(is_superadmin=False)
    total_user = users.count()
    pending_delivery = Order.objects.filter(
        Q(status="Accepted") | Q(status="New") | Q(status="Processing")
    ).count()
    request_refunds = Order.objects.filter(
        refund_requested=True, refund_granted=False
    )
    request_refunds_count = request_refunds.count()
    orders = Order.objects.filter(status="Completed")
    total_order = orders.count()
    revenue = orders.aggregate(total_revenue=Sum("order_total"))[
        "total_revenue"
    ]
    orders = Order.objects.filter(
        Q(status="Accepted") | Q(status="New") | Q(status="Processing")
    ).order_by("-created_at")[:4]
    if revenue is not None:
        revenue = round(revenue, 2)
    else:
        revenue = 0
    labels = []
    data = []
    sales = (
        Order.objects.filter(status="Completed")
        .annotate(day=ExtractDay("created_at"))
        .annotate(month=ExtractMonth("created_at"))
        .values("day", "month")
        .annotate(total_orders=Count("order_total"))
        .annotate(total_sales=Sum("order_total"))
        .order_by("day")
    )
    for i in sales:
        labels.append(f'{i["month"]} {i["day"]}')
        data.append(i["total_orders"])
    context = {
        "total_stock": total_stock,
        "request_refunds": request_refunds,
        "request_refunds_count": request_refunds_count,
        "pending_delivery": pending_delivery,
        "total_user": total_user,
        "orders": orders,
        "users": users,
        "total_order": total_order,
        "revenue": revenue,
        "labels_json": json.dumps(labels),
        "data_json": json.dumps(data),
    }
    return render(
        request, "admin/adminbase/admin_dashboard.html", context
    )


# <<--------------------ADMIN ORDER MANAGEMENT------------------- -------->>


@user_passes_test(user_is_admin, login_url="/customadmin/adminlogin")
@login_required(login_url="/customadmin/adminlogin")
@never_cache
def order_management(request):
    orders = Order.objects.filter(is_ordered=True).order_by(
        "-created_at"
    )
    context = {
        "orders": orders,
    }
    return render(
        request, "admin/adminpages/order_management.html", context
    )


@user_passes_test(user_is_admin, login_url="/customadmin/adminlogin")
@login_required(login_url="/customadmin/adminlogin")
@never_cache
def change_order_status(request, order_id):
    order = Order.objects.get(order_number=order_id)
    user = order.user
    print(user)
    if request.method == "POST":
        status = request.POST["status"]
        order.status = status
        if order.status == "Cancelled" or order.status == "refunded":
            if order.payment.payment_method != "cod":
                wallet = Decimal(str(order.order_total))
                user.wallet += wallet
                user.save()
        order.save()
        messages.success(request, "Order status has been updated")
        return redirect(
            "order_management"
        )  # Redirect to the order list page after saving the changes
    else:
        order_form = OrderForm(instance=request.user)
    order_form = OrderForm(instance=order)
    context = {
        "orders": order,
        "order_form": order_form,
    }

    return render(
        request, "admin/adminpages/change_order_status.html", context
    )


@user_passes_test(user_is_admin, login_url="/customadmin/adminlogin")
@login_required(login_url="/customadmin/adminlogin")
@never_cache
def view_order_detail(request, order_id):
    current_user = request.user
    cart = Cart.objects.get(user=current_user)
    orders = Order.objects.get(order_number=order_id)
    order_product = OrderProduct.objects.filter(
        order__order_number=order_id
    )
    subtotal = 0
    for i in order_product:
        subtotal += i.product.price * i.quantity
    context = {
        "cart": cart,
        "orders": orders,
        "order_product": order_product,
        "subtotal": subtotal,
    }
    return render(
        request, "admin/adminpages/view_order_detail.html", context
    )


@user_passes_test(user_is_admin, login_url="/customadmin/adminlogin")
@login_required(login_url="/customadmin/adminlogin")
@never_cache
def admin_cancel_order(request, order_id):
    print("I was called")
    order = Order.objects.get(order_number=order_id)
    if order.status:
        print("I was here")
        order.status = "Cancelled"
        order.save()
        messages.success(request, "Order Cancelled Successfully.")
    return redirect("order_management")


@user_passes_test(user_is_admin, login_url="/customadmin/adminlogin")
@login_required(login_url="/customadmin/adminlogin")
@never_cache
def view_return_order(request, order_id):
    current_user = request.user
    cart = Cart.objects.get(user=current_user)
    orders = Order.objects.get(order_number=order_id)
    order_product = OrderProduct.objects.filter(
        order__order_number=order_id
    )
    refund = Refund.objects.get(order=orders)
    subtotal = 0
    for i in order_product:
        subtotal += i.product.price * i.quantity
    context = {
        "cart": cart,
        "orders": orders,
        "order_product": order_product,
        "subtotal": subtotal,
        "refund": refund,
    }
    return render(
        request, "admin/adminpages/view_return_order.html", context
    )


@user_passes_test(user_is_admin, login_url="/customadmin/admin_login")
@login_required(login_url="/customadmin/admin_login")
@never_cache
def admin_grant_return_request(request, order_id):
    order = Order.objects.get(order_number=order_id)
    user = Account.objects.get(id=order.user.id)
    if order.refund_requested == True and order.refund_granted == False:
        order.refund_granted = True
        order.status = "refunded"
        wallet = Decimal(str(order.order_total))
        user.wallet += wallet
        user.save()
        order.save()
    return redirect("order_management")


# <<--------------------ADMIN COUPON MANAGEMENT------------------- -------->>


@user_passes_test(user_is_admin, login_url="/customadmin/adminlogin")
@login_required(login_url="/customadmin/adminlogin")
@never_cache
def coupon(request):
    coupons = Coupon.objects.all()
    context = {
        "coupons": coupons,
    }
    return render(request, "admin/adminpages/coupon.html", context)


@user_passes_test(user_is_admin, login_url="/customadmin/adminlogin")
@login_required(login_url="/customadmin/adminlogin")
@never_cache
def add_coupon(request):
    if request.method == "POST":
        coupon = Coupon()
        coupon_code = request.POST["coupon_code"]
        if Coupon.objects.filter(coupon_code=coupon_code):
            messages.error(request, "Coupon already exists")
            return redirect("add_coupon")
        else:
            coupon.coupon_code = coupon_code
            coupon.minimum_amount = request.POST["minimum_amount"]
            coupon.discount_price = request.POST["discount"]
            coupon.save()
            return redirect("coupon")
    else:
        return render(request, "admin/adminpages/add_coupon.html")


@user_passes_test(user_is_admin, login_url="/customadmin/adminlogin")
@login_required(login_url="/customadmin/adminlogin")
@never_cache
def edit_coupon(request, pk):
    coupon = get_object_or_404(Coupon, pk=pk)
    if request.method == "POST":
        coupon.coupon_code = request.POST.get("coupon_code")
        coupon.discount_price = request.POST.get("discount")
        coupon.minimum_amount = request.POST.get("minimum_amount", 0)
        coupon.save()
        messages.success(request, "Coupon updated successfully!")
        return redirect("coupon")
    return render(
        request, "admin/adminpages/edit_coupon.html", {"coupon": coupon}
    )


@user_passes_test(user_is_admin, login_url="/customadmin/adminlogin")
@login_required(login_url="/customadmin/adminlogin")
def undelete_coupon(request, pk):
    coupon = get_object_or_404(Coupon, pk=pk)
    coupon.is_expired = False
    coupon.save()
    return redirect("coupon")


@user_passes_test(user_is_admin, login_url="/customadmin/adminlogin")
@login_required(login_url="/customadmin/adminlogin")
def delete_coupon(request, pk):
    coupon = get_object_or_404(Coupon, pk=pk)
    coupon.is_expired = True
    coupon.save()
    return redirect("coupon")


@user_passes_test(user_is_admin, login_url="/customadmin/adminlogin")
@login_required(login_url="/customadmin/adminlogin")
@never_cache
def view_returt_list(request):
    orders = Order.objects.filter(status="hold").order_by("-created_at")
    context = {
        "orders": orders,
    }
    return render(
        request, "admin/adminpages/view_returt_list.html", context
    )
