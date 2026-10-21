from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import Order

@shared_task
def send_order_confirmation(order_id):
    order = (Order.objects.select_related("user").prefetch_related("items__asset").get(id=order_id))
    subject = f"Order Confirmation - Order #{order.id}"
    html_message = render_to_string(
        "emails/order_confirmation.html",
        {
            "order": order,
        }
    )
    email = EmailMultiAlternatives(
        subject=subject,
        body=f"Your order #{order.id} has been successfully placed.",
        from_email="noreply@digitalmarketplace.com",
        to=[order.user.email],
    )
    email.attach_alternative(html_message, "text/html")
    email.send()
    return f"Order confirmation sent for order #{order.id}"