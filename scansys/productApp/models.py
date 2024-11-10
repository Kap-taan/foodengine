from django.db import models

# Create your models here.
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.conf import settings
from enum import Enum

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class ProductType(models.TextChoices):
    VEG = "Veg", "Veg"
    NON_VEG = "Non Veg", "Non Veg"

class Product(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='product_images/')
    creation_time = models.DateTimeField(default=timezone.now)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    ingredients = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_price_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_product_id = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=7, choices=ProductType.choices, default=ProductType.VEG)

    def __str__(self):
        return self.name


class OrderStatus(Enum):
    ACCEPTED = 'Accepted'
    COOKING = 'Cooking'
    READY = 'Ready'
    WAITING = 'Waiting'
    FAILED = 'Failed'
    COMPLETED = 'Completed'

    @classmethod
    def choices(cls):
        return [(status.value, status.name) for status in cls]

class PaymentStatus(models.TextChoices):
    PENDING = 'Pending', 'Pending'
    COMPLETED = 'Completed', 'Completed'
    FAILED = 'Failed', 'Failed'

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    products = models.ManyToManyField('Product', related_name='orders', through='OrderProduct')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=10, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    stripe_checkout_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    seat_number = models.CharField(max_length=10, blank=True, null=True)  # New field for seat number
    order_status = models.CharField(max_length=10, choices=OrderStatus.choices(), default=OrderStatus.ACCEPTED.value)  # New field
    comment = models.TextField(blank=True, null=True)  # New field for comments

    def __str__(self):
        return f"Order {self.id} by {self.user}"

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in order {self.order.id}"

class CartItem(models.Model):
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"
    
class Seat(models.Model):
    seat_number = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.seat_number