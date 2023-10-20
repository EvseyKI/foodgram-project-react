from django.contrib import admin
from django import forms

from .models import (User, Subscription)


class SubscribeForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ('user', 'author',)

    def clean(self):
        subscribe = Subscription.objects.filter(
            user=self.cleaned_data['user'],
            author=self.cleaned_data['author']
        )
        if subscribe.exists():
            raise forms.ValidationError(
                'Подписка уже существует')
        if self.cleaned_data['user'] == self.cleaned_data['author']:
            raise forms.ValidationError(
                'Хотел подписаться сам на себя? плак плак')
        return self.cleaned_data


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
    form = SubscribeForm
