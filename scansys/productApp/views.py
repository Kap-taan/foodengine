from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Product, Order, Cart, CartItem, Seat
from .serializers import ProductSerializer, OrderSerializer, CartSerializer, SeatSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated

# View to get all products
class ProductListView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

# View to get all orders for a specific user
class UserOrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get orders for the authenticated user
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

# View to get details of products based on IDs in the request body
class ProductDetailByIDsView(APIView):
    def post(self, request):
        product_ids = request.data.get('product_ids', [])
        products = Product.objects.filter(id__in=product_ids)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class UserCartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def post(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        items = request.data.get('items', [])  # Expecting a list of {'product_id': <id>, 'quantity': <qty>}
        
        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 1)  # Default quantity to 1 if not provided
            
            # Check if the product exists
            product = Product.objects.filter(id=product_id).first()
            if product:
                cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
                cart_item.quantity = quantity  # Increment the quantity
                cart_item.save()
            else:
                return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        items = request.data.get('items', [])  # Expecting a list of {'product_id': <id>}
        
        for item in items:
            product_id = item.get('product_id')
            
            # Check if the product exists in cart items
            cart_item = CartItem.objects.filter(cart=cart, product__id=product_id).first()
            if cart_item:
                cart_item.delete()  # Remove the cart item
            else:
                return Response({"error": "Product not found in cart."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        """
        Edit the quantity of a product in the cart.
        Expecting data like {'product_id': <id>, 'quantity': <new_quantity>}
        """
        cart, created = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        new_quantity = request.data.get('quantity')

        # Check if the product exists in the cart items
        cart_item = CartItem.objects.filter(cart=cart, product__id=product_id).first()
        if cart_item:
            if new_quantity is not None and new_quantity >= 0:
                cart_item.quantity = new_quantity  # Update the quantity
                cart_item.save()
                return Response({"message": "Quantity updated successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid quantity."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Product not found in cart."}, status=status.HTTP_404_NOT_FOUND)
        
class SeatListView(APIView):
    def get(self, request):
        seats = Seat.objects.all()
        serializer = SeatSerializer(seats, many=True)
        return Response(serializer.data)