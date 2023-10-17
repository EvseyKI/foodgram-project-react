from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import (MinValueValidator,
                                    MaxValueValidator,
                                    RegexValidator)

from foodgram.settings import MAX_LENGTH_NAME_TAG

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        'Тeг',
        max_length=200,
        unique=True,
        help_text='Название тeга',
    )
    color = models.CharField(
        'Цвет в HEX',
        max_length=7,
        help_text='Цвет в HEX',
        validators=(
            RegexValidator(
                regex=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Нужен только HEX формат'
            ),
        )
    )
    slug = models.SlugField(
        'Слаг',
        max_length=200,
        unique=True,
        help_text='slug',
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return (self.name if len(self.name) < MAX_LENGTH_NAME_TAG
                else self.name[:MAX_LENGTH_NAME_TAG] + "...")


class Ingredient(models.Model):
    name = models.CharField(
        'Ингредиент',
        max_length=200,
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=200,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name="unique_ingredient"
            ),
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        'Название рецепта',
        max_length=200,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientLink',
        related_name='recipes',
        verbose_name='Список ингредиентов',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Список id тегов',
    )
    image = models.ImageField(
        'Картинка, закодированная в Base64',
    )
    text = models.TextField(
        'Описание'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (в минутах)',
        validators=(
            MinValueValidator(1),
            MaxValueValidator(500),
        ),
    )
    pub_date = models.DateTimeField(
        'Дата публикации рецепта',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientLink(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='link_of_ingredients',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='link_of_ingredients',
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество ингредиентов',
        validators=(
            MinValueValidator(1),
            MaxValueValidator(500),
        ),
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name="unique_ingredientlink"
            ),
        ]

    def __str__(self):
        return f'{self.recipe.name}, {self.ingredient.name}-{self.amount}'


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name="unique_favorite_recipe"
            ),
        ]

    def __str__(self):
        return f'Рецепт {self.recipe} в избранных у {self.user}'


class ShoppingList(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='Рецепт',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='Пользователь',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name="unique_shopping_list"
            ),
        ]

    def __str__(self):
        return f'Рецепт {self.recipe} в списке покупок у {self.user}'
