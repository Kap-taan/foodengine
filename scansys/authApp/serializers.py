from rest_framework import serializers
from .models import MyUser

class MyUserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = MyUser
        fields = ['id', 'email', 'first_name', 'last_name', 'type']  # Add any other fields you need

    def get_type(self, obj):
        return obj.get_type_display()  # Returns the display name for the type