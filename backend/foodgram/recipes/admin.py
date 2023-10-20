from django.contrib import admin
from django.contrib.auth.models import Group
from django import forms
from django.core.exceptions import ValidationError
from rest_framework.authtoken.models import TokenProxy

from .models import (
    Tag, Ingredient, Recipe,
    IngredientLink, Favorite,
    ShoppingList,
)


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ('name', 'slug', 'color',)

    def clean(self):
        tag = Tag.objects.filter(color=self.cleaned_data['color'].upper())
        if tag.exists():
            raise forms.ValidationError('Тэг с таким цветом уже сущесвтует')
        self.cleaned_data['color'] = self.cleaned_data['color'].upper()
        return self.cleaned_data


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug',)
    search_fields = ('name',)
    list_filter = ('slug',)
    form = TagForm


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('measurement_unit',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe',)
    search_fields = ('user',)
    list_filter = ('user',)


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe',)
    search_fields = ('user',)
    list_filter = ('user',)


class IngredientLinkInline(admin.TabularInline):
    model = IngredientLink
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author',)
    search_fields = ('name', 'author',)
    inlines = (IngredientLinkInline,)

    def save_formset(self, request, form, formset, change):
        can_delete = False
        for ingredient in formset.cleaned_data:
            if not ingredient.get('DELETE', True):
                can_delete = True
                break
        if not can_delete:
            raise ValidationError('Нельзя удалить все ингредиенты')
        return super().save_formset(request, form, formset, change)


admin.site.unregister(Group)
admin.site.unregister(TokenProxy)
