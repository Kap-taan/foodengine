# admin.py

from django.contrib import admin
from unfold.admin import ModelAdmin  # Import ModelAdmin from Unfold
from .models import MyUser

@admin.register(MyUser)
class MyUserAdmin(ModelAdmin):
    pass
