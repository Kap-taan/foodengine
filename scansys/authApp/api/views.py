from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import UserRegistrationSerializer
from rest_framework import status

# @api_view(['POST'])
# def createUserProfile(request):
#     serializer = UserRegistrationSerializer(data = request.data, many = False)
#     serializer.is_valid(raise_exception=True)
#     user = serializer.save()
#     data = "hello world"
#     token = RefreshToken.for_user(user)
#     data = serializer.data
#     data["tokens"] = {"refresh":str(token),
#                           "access": str(token.access_token)}
#     return Response(data, status= status.HTTP_201_CREATED)