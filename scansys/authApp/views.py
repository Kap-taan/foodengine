from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from authApp.serializers import MyUserSerializer
from .models import MyUser
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import IsAuthenticated
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework.authentication import TokenAuthentication

class UserRegistrationView(APIView):
    def post(self, request):
        email = request.data.get('email')
        username = request.data.get('username')
        first_name = request.data.get('first_name')
        password = request.data.get('password')

        # Validate input data
        if not email or not username or not password:
            return Response({'error': 'Email, username, and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate email format
        try:
            validate_email(email)  # This will raise ValidationError if the email is invalid
        except ValidationError:
            return Response({'error': 'Invalid email format.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user already exists
        if MyUser.objects.filter(email=email).exists():
            return Response({'error': 'User with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create the user
        user = MyUser(
            email=email,
            username=username,
            first_name=first_name,
            password=make_password(password)  # Hash the password
        )
        user.save()

        return Response({'message': 'User created successfully.'}, status=status.HTTP_201_CREATED)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user  # Get the authenticated user
        serializer = MyUserSerializer(user)  # Serialize user data
        return Response(serializer.data)  # Return serialized data
    
class VerifyTokenView(APIView):
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # If the token is valid, request.user will be set and authentication will pass
        return Response({"message": "Token is valid."}, status=status.HTTP_200_OK)
