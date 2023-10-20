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
        method = self.Meta.formfield_callback.keywords['request'].path_info
        if tag.exists() and 'add' == method.split('/')[-2]:
            raise forms.ValidationError('Тэг с таким цветом уже сущесвтует')
        self.cleaned_data['color'] = self.cleaned_data['color'].upper()
        return self.cleaned_data


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = '__all__'

    def clean(self):
        data_keys = self.data.keys()
        count_delete = 0
        for item in data_keys:
            if 'DELETE' in item:
                count_delete += 1
        if count_delete == self.instance.link_of_ingredients.count():
            raise ValidationError('Нельзя удалить все ингредиенты')
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
    form = RecipeForm


admin.site.unregister(Group)
admin.site.unregister(TokenProxy)
