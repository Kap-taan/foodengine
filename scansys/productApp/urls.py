from django.urls import path
from .views import ProductListView, SeatListView, UserOrderListView, ProductDetailByIDsView, UserCartView

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product-list'),
    path('orders/', UserOrderListView.as_view(), name='user-order-list'),
    path('products-by-ids/', ProductDetailByIDsView.as_view(), name='product-detail-by-ids'),
    path('cart/', UserCartView.as_view(), name='user-cart'),
    path('seats/', SeatListView.as_view(), name='seat-list'),
]
