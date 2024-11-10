from rest_framework import serializers
from .models import Product, Order, Cart, CartItem, OrderProduct, Seat

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name', read_only=True)
    type = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'image', 'creation_time', 'category', 'ingredients', 'price', 'stripe_price_id', 'stripe_product_id', 'description', 'type']


class ProductInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'image', 'price', 'description', 'type']

class OrderProductSerializer(serializers.ModelSerializer):
    product = ProductInfoSerializer()
    price_at_purchase = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity = serializers.IntegerField()

    class Meta:
        model = OrderProduct
        fields = ['product', 'price_at_purchase', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(source='orderproduct_set', many=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_status = serializers.CharField()
    seat_number = serializers.CharField()
    order_status = serializers.CharField()  # Add order_status field
    comment = serializers.CharField(required=False, allow_blank=True)  # Add comment field

    class Meta:
        model = Order
        fields = ['id', 'created_at', 'total_amount', 'payment_status', 'stripe_checkout_id', 'products', 'seat_number', 'order_status', 'comment']


        
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()  # Include product details

    class Meta:
        model = CartItem
        fields = ['product', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'cart_items', 'created_at']

class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ['id', 'seat_number']