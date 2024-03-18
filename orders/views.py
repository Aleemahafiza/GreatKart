from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from carts.models import CartItem
from store.models import Coupon
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
from django.template.loader import render_to_string
import datetime
import json
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from datetime import datetime, date
import datetime
from accounts.models import Address
from orders.forms import AddressForm, RefundForm
from django.urls import reverse


def shipping_address(request):
    current_user = request.user
    if request.method == "POST":
        print("inside post if")
        form = AddressForm(request.POST)
        if form.is_valid():
            print("inside is_valid if")
            data = Address()
            data.user = current_user
            data.first_name = form.cleaned_data["first_name"]
            data.last_name = form.cleaned_data["last_name"]
            data.phone = form.cleaned_data["phone"]
            data.email = form.cleaned_data["email"]
            data.address_line_1 = form.cleaned_data["address_line_1"]
            data.address_line_2 = form.cleaned_data["address_line_2"]
            data.country = form.cleaned_data["country"]
            data.state = form.cleaned_data["state"]
            data.city = form.cleaned_data["city"]
            data.save()
            messages.success(request, "Address added successfully")
            referrer = request.session.pop("referrer", "")
            print(referrer)
            if referrer == "checkout":
                print("tehere")
                checkout_url = reverse("checkout")
                return redirect(checkout_url)
            else:
                print("here")
                return redirect("my_address")
        else:
            messages.error(request, "Invalid")

    else:
        form = AddressForm()
    context = {
        "form": form,
    }
    return render(request, "store/shipping_address.html", context)


def payments(request):

    body = json.loads(request.body)
    order = Order.objects.get(
        user=request.user,
        is_ordered=False,
        order_number=body["orderID"],
    )

    # Store transaction details inside Payment model
    payment = Payment(
        user=request.user,
        payment_id=body["transID"],
        payment_method=body["payment_method"],
        amount_paid=order.order_total,
        status=body["status"],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move the cart items to Order Product table
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()
        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()
        print("variations:", product_variation)
        for variation in item.variations.all():
            variation.quantity -= item.quantity
            variation.save()

    # Clear cart
    CartItem.objects.filter(user=request.user).delete()

    # Send order recieved email to customer
    mail_subject = "Thank you for your order!"
    message = render_to_string(
        "orders/order_recieved_email.html",
        {
            "user": request.user,
            "order": order,
        },
    )
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    # Send order number and transaction id back to sendData method via JsonResponse
    data = {
        "order_number": order.order_number,
        "transID": payment.payment_id,
    }
    return JsonResponse(data)


from django.shortcuts import render, redirect
from .models import Order
from .forms import OrderForm
import datetime
from carts.models import Cart
from .models import OrderAddress


def place_order(request, total=0, quantity=0):
    current_user = request.user
    cart = Cart.objects.get(user=current_user)

    # If the cart is empty redirect back to store
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect("store")
    grand_total, total, quantity, tax = cart.calculate_grand_total()

    if request.method == "POST":
        data = Order()
        data.user = current_user
        address_id = request.POST["address_id"]
        address = Address.objects.get(id=address_id)
        if cart.coupon is not None:
            data.coupon_discount = cart.coupon.discount_price
        order_address = OrderAddress.objects.create(
            full_name=address.full_name(),
            phone=address.phone,
            email=address.email,
            full_address=address.full_address(),
            country=address.country,
            state=address.state,
            city=address.city,
        )
        data.address = order_address
        data.order_note = request.POST["order_note"]
        data.order_total = grand_total
        data.tax = tax
        data.ip = request.META.get("REMOTE_ADDR")
        data.save()

        # Generate order number
        yr = int(datetime.date.today().strftime("%Y"))
        dt = int(datetime.date.today().strftime("%d"))
        mt = int(datetime.date.today().strftime("%m"))
        d = datetime.date(yr, mt, dt)
        current_date = d.strftime("%Y%m%d")
        order_number = current_date + str(data.id)
        data.order_number = order_number
        data.save()

        order = Order.objects.get(
            user=current_user,
            is_ordered=False,
            order_number=order_number,
        )

        context = {
            "cart": cart,
            "order": order,
            "cart_items": cart_items,
            "total": total,
            "tax": tax,
            "grand_total": grand_total,
        }
        # Check if order total is above Rs 1000
        if grand_total > 1000:
            return render(
                request, "orders/not_available_for_cod.html", context
            )

        return render(request, "orders/payments.html", context)
    else:
        return redirect("checkout")


from django.shortcuts import redirect


def order_complete(request):
    current_user = request.user
    cart = Cart.objects.get(user=current_user)
    order_number = request.GET.get("order_number")
    transID = request.GET.get("payment_id")

    try:
        order = Order.objects.get(
            order_number=order_number, is_ordered=True
        )
        ordered_products = OrderProduct.objects.filter(
            order_id=order.id
        )
        payment_method = "PayPal"
        subtotal = sum(
            item.product_price * item.quantity
            for item in ordered_products
        )
        payment = Payment.objects.get(payment_id=transID)

        for item in ordered_products:
            item.total_price = item.product_price * item.quantity

        context = {
            "cart": cart,
            "total_price": item.total_price,
            "order": order,
            "ordered_products": ordered_products,
            "order_number": order.order_number,
            "transID": payment.payment_id,
            "payment": payment,
            "subtotal": subtotal,
            "payment_method": payment_method,
        }
        return render(request, "orders/order_complete.html", context)
    except (Order.DoesNotExist, Payment.DoesNotExist):
        return redirect("home")


import logging

logger = logging.getLogger(__name__)


def cod(request, order_number):
    current_user = request.user

    try:
        order = Order.objects.get(
            user=current_user, is_ordered=False, id=order_number
        )

        order.status = "New"
        payment_method = "Cash On Delivery"
        order.is_ordered = True
        order.save()

        # Move the cart item into the order product table
        cart_items = CartItem.objects.filter(user=current_user)
        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order_id = order.id
            orderproduct.user_id = request.user.id
            orderproduct.product_id = item.product_id
            orderproduct.quantity = item.quantity
            orderproduct.product_price = item.product.price
            orderproduct.ordered = True
            orderproduct.save()

            cart_item = CartItem.objects.get(id=item.id)

            product_variation = cart_item.variations.all()
            orderproduct = OrderProduct.objects.get(id=orderproduct.id)
            orderproduct.variations.set(product_variation)
            orderproduct.save()

            for variation in item.variations.all():
                variation.quantity -= item.quantity
                variation.save()

        # Clear the cart
        CartItem.objects.filter(user=request.user).delete()

        # Send the order received email to the customer
        mail_subject = "Thank you for your order"
        message = render_to_string(
            "orders/order_recieved_email.html",
            {
                "user": request.user,
                "order": order,
            },
        )
        to_email = request.user.email
        send_email = EmailMessage(mail_subject, message, to=[to_email])
        send_email.send()

        order_number = order.order_number
        request.session["order_number"] = order_number
        return redirect(
            "cod_order_complete",
            order_number=order.id,
        )

    except Order.DoesNotExist:
        logger.error(
            f"Order not found for Order ID: {order_number}, Current User: {current_user}"
        )
        raise


def cod_order_complete(request, order_number):
    current_user = request.user
    cart = Cart.objects.get(user=current_user)

    try:
        order = Order.objects.get(
            user=current_user, id=order_number, is_ordered=True
        )
        ordered_products = OrderProduct.objects.filter(
            order_id=order.id
        )
        payment_method = "Cash On Delivery"

        for item in ordered_products:
            item.total_price = item.product_price * item.quantity

        context = {
            "cart": cart,
            "payment_method": payment_method,
            "total_price": item.total_price,
            "order": order,
            "ordered_products": ordered_products,
            "order_number": order.order_number,
            "payment_method": payment_method,
        }
        return render(request, "orders/cod_complete.html", context)

    except Order.DoesNotExist:
        logger.error(
            f"Order not found for Order Number: {order_number}"
        )
        raise


from django.shortcuts import get_object_or_404, render
from io import BytesIO
from reportlab.pdfgen import canvas


def download_invoice_paypal(request, order_number):
    # Retrieve the order
    order = get_object_or_404(Order, order_number=order_number)
    current_user = request.user
    cart = Cart.objects.get(user=current_user)
    ordered_products = OrderProduct.objects.filter(order_id=order.id)
    payment_method = "PayPal"
    subtotal = sum(
        item.product_price * item.quantity for item in ordered_products
    )

    total_discount_amount = sum(
        (cart_item.coupon.discount_price if cart_item.coupon else 0)
        for cart_item in cart.cartitem_set.all()
    )

    # Create a BytesIO buffer to store the PDF
    buffer = BytesIO()

    # Create the PDF object, using the BytesIO buffer as its "file."
    pdf = canvas.Canvas(buffer)

    # Set the font for the PDF
    pdf.setFont("Helvetica", 12)

    # Add a heading
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(100, 800, "GreatKart Invoice")

    # Add a subheading
    pdf.setFont("Helvetica", 14)
    pdf.drawString(100, 780, f"Invoice for Order #{order.order_number}")

    # Add a box around the order details
    pdf.rect(80, 740, 450, 200)

    # Starting y-position for content inside the box
    y_position = 720

    # Invoiced To
    pdf.drawString(100, y_position, "Invoiced To:")
    y_position -= 15
    pdf.drawString(120, y_position, f"{order.address.full_name}")
    y_position -= 15
    pdf.drawString(120, y_position, f"{order.address.full_address}")
    y_position -= 15
    pdf.drawString(
        120, y_position, f"{order.address.city}, {order.address.state}"
    )
    y_position -= 15
    pdf.drawString(120, y_position, f"{order.address.country}")
    y_position -= 15
    pdf.drawString(120, y_position, f"Phone: {order.address.phone}")
    y_position -= 15
    pdf.drawString(120, y_position, f"Email: {order.address.email}")
    y_position -= 30

    # Draw a line after invoiced to details
    pdf.line(100, y_position, 530, y_position)
    y_position -= 30

    # Order Details
    pdf.drawString(100, y_position, "Order Details:")
    y_position -= 15
    pdf.drawString(120, y_position, f"Order: #{order_number}")
    y_position -= 15
    pdf.drawString(120, y_position, f"Transaction ID: {order.payment}")
    y_position -= 15
    pdf.drawString(120, y_position, f"Order Date: {order.created_at}")
    y_position -= 15
    pdf.drawString(
        120, y_position, f"Payment Status: {order.payment.status}"
    )
    y_position -= 15
    pdf.drawString(120, y_position, f"Payment Method: {payment_method}")
    y_position -= 30
    # Draw a line after order details
    pdf.line(100, y_position, 530, y_position)
    y_position -= 30

    # Ordered Products
    pdf.drawString(100, y_position, "Ordered Products:")
    y_position -= 15

    for item in ordered_products:
        product_info = f"{item.product.product_name} - {item.quantity} x ${item.product_price} = ${item.product_price * item.quantity}"
        pdf.drawString(120, y_position, product_info)
        y_position -= 15

    # Draw a line after ordered products
    pdf.line(100, y_position, 530, y_position)
    y_position -= 10

    # Total Box

    pdf.drawString(100, y_position - 40, f"Subtotal: ${subtotal}")
    pdf.drawString(100, y_position - 60, f"Tax: ${order.tax}")
    pdf.drawString(
        100, y_position - 80, f"Grand Total: ${order.order_total}"
    )

    y_position -= 30

    # Thank you message
    pdf.drawString(
        100, y_position - 100, "Thank you for shopping with us!"
    )

    # Save the PDF to the buffer
    pdf.showPage()
    pdf.save()

    # Set the buffer's position to the beginning
    buffer.seek(0)

    # Create a response object with the PDF
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f"attachment; filename=invoice_{order_number}.pdf"
    )
    response.write(buffer.read())

    return response


def download_invoice_cod(request, order_number):
    # Retrieve the order
    order = get_object_or_404(Order, order_number=order_number)
    current_user = request.user
    cart = Cart.objects.get(user=current_user)
    ordered_products = OrderProduct.objects.filter(order_id=order.id)
    payment_method = "Cash On Delivery"
    subtotal = sum(
        item.product_price * item.quantity for item in ordered_products
    )

    total_discount_amount = sum(
        (cart_item.coupon.discount_price if cart_item.coupon else 0)
        for cart_item in cart.cartitem_set.all()
    )

    # Create a BytesIO buffer to store the PDF
    buffer = BytesIO()

    # Create the PDF object, using the BytesIO buffer as its "file."
    pdf = canvas.Canvas(buffer)

    # Set the font for the PDF
    pdf.setFont("Helvetica", 12)

    # Add a heading
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(100, 800, "GreatKart Invoice")

    # Add a subheading
    pdf.setFont("Helvetica", 14)
    pdf.drawString(100, 780, f"Invoice for Order #{order.order_number}")

    # Add a box around the order details
    pdf.rect(80, 740, 450, 200)

    # Starting y-position for content inside the box
    y_position = 720

    # Invoiced To
    pdf.drawString(100, y_position, "Invoiced To:")
    y_position -= 15
    pdf.drawString(120, y_position, f"{order.address.full_name}")
    y_position -= 15
    pdf.drawString(120, y_position, f"{order.address.full_address}")
    y_position -= 15
    pdf.drawString(
        120, y_position, f"{order.address.city}, {order.address.state}"
    )
    y_position -= 15
    pdf.drawString(120, y_position, f"{order.address.country}")
    y_position -= 15
    pdf.drawString(120, y_position, f"Phone: {order.address.phone}")
    y_position -= 15
    pdf.drawString(120, y_position, f"Email: {order.address.email}")
    y_position -= 30

    # Draw a line after invoiced to details
    pdf.line(100, y_position, 530, y_position)
    y_position -= 30

    # Order Details
    pdf.drawString(100, y_position, "Order Details:")
    y_position -= 15
    pdf.drawString(120, y_position, f"Order: #{order_number}")
    y_position -= 15
    pdf.drawString(120, y_position, f"Order Date: {order.created_at}")
    y_position -= 15
    pdf.drawString(120, y_position, f"Payment Method: {payment_method}")
    y_position -= 30
    # Draw a line after order details
    pdf.line(100, y_position, 530, y_position)
    y_position -= 30

    # Ordered Products
    pdf.drawString(100, y_position, "Ordered Products:")
    y_position -= 15

    for item in ordered_products:
        product_info = f"{item.product.product_name} - {item.quantity} x ${item.product_price} = ${item.product_price * item.quantity}"
        pdf.drawString(120, y_position, product_info)
        y_position -= 15

    # Draw a line after ordered products
    pdf.line(100, y_position, 530, y_position)
    y_position -= 10

    # Total Box

    pdf.drawString(100, y_position - 40, f"Subtotal: ${subtotal}")
    pdf.drawString(100, y_position - 60, f"Tax: ${order.tax}")
    pdf.drawString(
        100, y_position - 80, f"Grand Total: ${order.order_total}"
    )

    y_position -= 30

    # Thank you message
    pdf.drawString(
        100, y_position - 100, "Thank you for shopping with us!"
    )

    # Save the PDF to the buffer
    pdf.showPage()
    pdf.save()

    # Set the buffer's position to the beginning
    buffer.seek(0)

    # Create a response object with the PDF
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f"attachment; filename=invoice_{order_number}.pdf"
    )
    response.write(buffer.read())

    return response
