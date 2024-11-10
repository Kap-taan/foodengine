from django.urls import path
from .views import StripeCheckoutView, StripePaymentStatusUpdateView


urlpatterns = [
    path('stripe/create-checkout-session', StripeCheckoutView.as_view()),
    path('stripe/update-payment-status', StripePaymentStatusUpdateView.as_view(), name='update-payment-status'),
]
