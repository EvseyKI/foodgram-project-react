from django.contrib import admin

from .models import (User, Subscription)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'username', 'first_name', 'last_name',)
    search_fields = ('username',)
    list_filter = ('username', 'email',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author',)
    search_fields = ('author',)
    search_fields = ('user__username', 'author__username',)
