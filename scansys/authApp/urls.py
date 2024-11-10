from django.urls import path
from .views import UserRegistrationView, UserProfileView
from .views import VerifyTokenView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('verify-token', VerifyTokenView.as_view(), name='verify-token'),
]
