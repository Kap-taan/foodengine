import json
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect
from productApp.models import Order, Product, OrderProduct  # Ensure Order and Product models are imported
from rest_framework.permissions import IsAuthenticated

import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripePaymentStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Check if the user is a waiter
        if request.user.type == 3:
            return Response({"message": "No payment update required for waiters."}, status=status.HTTP_201_CREATED)
        
        # Retrieve list of checkout IDs from request data
        checkout_ids = request.data.get('checkout_ids', [])
        
        if not isinstance(checkout_ids, list) or not checkout_ids:
            return Response({"error": "A non-empty list of checkout_ids is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        results = []
        
        for checkout_id in checkout_ids:
            try:
                # Retrieve the checkout session from Stripe
                checkout_session = stripe.checkout.Session.retrieve(checkout_id)

                # Check if the payment was successful
                if checkout_session.payment_status == 'paid':
                    # Update the payment status and order status of all orders with the same checkout_id
                    orders = Order.objects.filter(stripe_checkout_id=checkout_id)
                    
                    if not orders.exists():
                        results.append({"checkout_id": checkout_id, "status": "not_found"})
                        continue

                    # Update payment status and set order_status to 'Accepted' for all matching orders
                    orders.update(payment_status='COMPLETED', order_status='Accepted')
                    results.append({"checkout_id": checkout_id, "status": "completed"})

                else:
                    # If payment is not completed, update the status of all orders to 'FAILED'
                    orders = Order.objects.filter(stripe_checkout_id=checkout_id)
                    if not orders.exists():
                        results.append({"checkout_id": checkout_id, "status": "not_found"})
                        continue

                    # Update payment status for all matching orders
                    orders.update(payment_status='FAILED', order_status='WAITING')  # Assuming the default status is WAITING
                    results.append({"checkout_id": checkout_id, "status": "failed"})

            except stripe.error.StripeError as e:
                # Log Stripe errors for each checkout_id
                print(f"Stripe error for checkout_id {checkout_id}: {e}")
                results.append({"checkout_id": checkout_id, "status": "stripe_error", "error": str(e)})
            except Exception as e:
                # Log unexpected errors for each checkout_id
                print(f"Unexpected error for checkout_id {checkout_id}: {e}")
                results.append({"checkout_id": checkout_id, "status": "error", "error": str(e)})

        return Response({"results": results}, status=status.HTTP_200_OK)


class StripeCheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Parse and validate request data
            body_data = request.data

            # Check that 'items' field is present and is a list
            if 'items' not in body_data or not isinstance(body_data['items'], list) or not body_data['items']:
                raise ValueError("Request data must contain an 'items' field with a non-empty list.")
            
            # Check if 'seat_number' is present for the order
            seat_number = body_data.get('seat_number', None)
            if seat_number and not isinstance(seat_number, str):
                raise ValueError("Seat number must be a string.")
            
            # Check if 'comment' is present and valid (optional)
            comment = body_data.get('comment', None)
            if comment and not isinstance(comment, str):
                raise ValueError("Comment must be a string.")
            
            validated_items = []
            total_amount = 0  # Track total amount for the order

            for item in body_data['items']:
                # Validate item structure
                if not isinstance(item, dict) or 'price' not in item or 'quantity' not in item:
                    raise ValueError("Each item must contain 'price' and 'quantity' fields.")
                
                # Retrieve product information from Stripe or database
                price_id = item['price']
                quantity = item['quantity']

                # If user is a waiter, use the database product directly
                if request.user.type == 3:
                    product_obj = Product.objects.get(stripe_price_id=price_id)
                else:
                    price_obj = stripe.Price.retrieve(price_id)
                    stripe_product_id = price_obj.product
                    product_obj = Product.objects.filter(stripe_product_id=stripe_product_id).first()
                    if not product_obj:
                        raise ValueError(f"No matching product found for Stripe product ID {stripe_product_id}")
                    total_amount += (price_obj.unit_amount * quantity / 100)  # Convert to currency units

                # Add validated item for creating the order
                validated_items.append({
                    'product': product_obj,
                    'quantity': quantity,
                    'price': product_obj.price  # Store current product price for consistency
                })

            # Default order status
            order_status = 'Waiting'  # Default for non-waiter users
            if request.user.type == 3:
                order_status = 'Accepted'
            print(order_status)
            # If user is a waiter, create the order without Stripe session
            if request.user.type == 3:
                order = Order.objects.create(
                    user=request.user,
                    total_amount=total_amount,
                    payment_status='PENDING',
                    stripe_checkout_id=None,  # No Stripe ID for waiter-created orders
                    seat_number=seat_number,  # Store seat number in order if provided
                    order_status=order_status,  # Set order_status to 'Accepted' for waiter
                    comment=comment  # Store the comment in the order
                )

                for item in validated_items:
                    OrderProduct.objects.create(
                        order=order,
                        product=item['product'],
                        price_at_purchase=item['price'],
                        quantity=item['quantity']
                    )

                return Response({"message": "Order created for waiter without payment processing."}, status=status.HTTP_201_CREATED)

            # For non-waiter users, create the Stripe checkout session
            checkout_session = stripe.checkout.Session.create(
                line_items=[{'price': item['product'].stripe_price_id, 'quantity': item['quantity']} for item in validated_items],
                invoice_creation={"enabled": True},
                mode='payment',
                success_url=settings.SITE_URL + '?success=true&session_id={CHECKOUT_SESSION_ID}',
                cancel_url=settings.SITE_URL + '?canceled=true',
            )

            # Create the order with the Stripe checkout session ID, seat_number, and comment
            order = Order.objects.create(
                user=request.user,
                total_amount=total_amount,
                payment_status='PENDING',
                stripe_checkout_id=checkout_session.id,
                seat_number=seat_number,  # Store seat number in order if provided
                order_status=order_status,  # Set order_status to 'WAITING' for non-waiter users
                comment=comment  # Store the comment in the order
            )

            # Save each product in OrderProduct with quantity and price at purchase
            for item in validated_items:
                OrderProduct.objects.create(
                    order=order,
                    product=item['product'],
                    price_at_purchase=item['price'],
                    quantity=item['quantity']
                )

            return Response({'url': checkout_session.url}, status=status.HTTP_200_OK)

        except ValueError as ve:
            print(f"Validation error: {ve}")
            return Response(
                {'error': str(ve)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print(f"Stripe Checkout Session creation error: {e}")
            return Response(
                {'error': 'Something went wrong when creating the Stripe checkout session'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
