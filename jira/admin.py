from django.contrib import admin

from .models import User, AppImage


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(AppImage)
class AppImageAdmin(admin.ModelAdmin):
    pass
