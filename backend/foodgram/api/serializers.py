import base64
from datetime import datetime
from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    Favorite,
    ShoppingList,
    IngredientLink,
)
from users.models import (User, Subscription)


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def to_representation(self, instance):
        data = super(UserSerializer, self).to_representation(instance)
        request = self.context.get('request')
        if request and request.method == 'GET':
            if self.context['request'].user.is_authenticated:
                data['is_subscribed'] = Subscription.objects.filter(
                    user=self.context['request'].user,
                    author=instance
                ).exists()
            else:
                data['is_subscribed'] = False
        else:
            data.pop('is_subscribed', None)
        return data

    def create(self, validated_data):
        return User.objects.create_user(
            username=self.validated_data['username'],
            email=self.validated_data['email'],
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name'],
            password=self.validated_data['password']
        )


class UserSetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField()
    current_password = serializers.CharField()

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.check_password(self.initial_data['current_password']):
            raise ValidationError('Текущий пароль не совпадает с базой')
        return attrs


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientLink
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class IngredientRecipeShortSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(required=True,
                                            queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientLink
        fields = (
            'id',
            'amount'
        )


class SmallRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscribeSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField(default=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    email = serializers.EmailField(read_only=True)
    username = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, instance):
        recipes = instance.recipes.all()
        recipes_limit = self.context['request'].query_params.get(
            'recipes_limit'
        )
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return SmallRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, instance):
        return instance.recipes.all().count()

    def validate(self, attrs):
        author = get_object_or_404(User, id=self.initial_data['id'])
        subscribe = Subscription.objects.filter(
            author=author, user=self.context['request'].user)
        if self.context['method'] == 'POST':
            if author == self.context['request'].user:
                raise ValidationError('Нельзя подписаться на самого себя')
            if subscribe.exists():
                raise ValidationError('Подписка уже существует')
        else:
            if not subscribe.exists():
                raise ValidationError('Подписка еще не существует')
        return attrs

    def create(self, validated_data):
        subscribe = Subscription.objects.create(
            author_id=self.initial_data['id'],
            user=self.context['request'].user)
        return subscribe.author


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_ingredients(self, instance):
        return IngredientRecipeSerializer(
            IngredientLink.objects.filter(recipe=instance),
            many=True
        ).data

    def get_is_favorited(self, instance):
        if not self.context['request'].user.is_authenticated:
            return False
        return Favorite.objects.filter(
            recipe=instance, user=self.context['request'].user
        ).exists()

    def get_is_in_shopping_cart(self, instance):
        if not self.context['request'].user.is_authenticated:
            return False
        return ShoppingList.objects.filter(
            recipe=instance, user=self.context['request'].user
        ).exists()


class FavoriteSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)
    cooking_time = serializers.IntegerField(read_only=True)
    image = serializers.ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )

    def validate(self, attrs):
        recipe = get_object_or_404(Recipe, id=self.initial_data['id'])
        favorite = Favorite.objects.filter(
            recipe=recipe, user=self.context['request'].user)
        if self.context['method'] == 'POST':
            if favorite.exists():
                raise ValidationError('Рецепт уже в избраном')
        else:
            if not favorite.exists():
                raise ValidationError('Рецепт еще не в избраном')
        return attrs

    def create(self, validated_data):
        favorite = Favorite.objects.create(
            recipe_id=self.initial_data['id'],
            user=self.context['request'].user)
        return favorite.recipe


class ShoppingListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)
    cooking_time = serializers.IntegerField(read_only=True)
    image = serializers.ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )

    def validate(self, attrs):
        recipe = get_object_or_404(Recipe, id=self.initial_data['id'])
        shopping_list = ShoppingList.objects.filter(
            recipe=recipe, user=self.context['request'].user)
        if self.context['method'] == 'POST':
            if shopping_list.exists():
                raise ValidationError('Рецепт уже в списке покупок')
        else:
            if not shopping_list.exists():
                raise ValidationError('Рецепт еще не в списке покупок')
        return attrs

    def create(self, validated_data):
        shopping_list = ShoppingList.objects.create(
            recipe_id=self.initial_data['id'],
            user=self.context['request'].user)
        return shopping_list.recipe


class PostUpdateRecipeSerializer(serializers.ModelSerializer):
    image = serializers.CharField(required=False)
    name = serializers.CharField(required=True)
    text = serializers.CharField(required=True)
    cooking_time = serializers.IntegerField(required=True)
    ingredients = IngredientRecipeShortSerializer(required=True, many=True)
    tags = serializers.PrimaryKeyRelatedField(
        required=True, many=True, queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )

    def convert_base64_to_image(self):
        type_image, image = self.validated_data['image'].split(';base64,')
        name = datetime.now().strftime("%Y%m%d%H%M%S")
        return ContentFile(
            base64.b64decode(image),
            name=f"{name}.{type_image.split('/')[-1]}"
        )

    def validate(self, data):
        cooking_time = int(self.initial_data['cooking_time'])
        if cooking_time < 1 or cooking_time > 500:
            raise ValidationError('Время приготовления должно быть > 1 < 500')
        ingredients_pk = [obj['id'] for obj in
                          self.initial_data['ingredients']]
        if len(ingredients_pk) > len(set(ingredients_pk)):
            raise ValidationError('Нужны только уникальные ингредиенты')
        if len(self.initial_data['tags']) > len(
                set(self.initial_data['tags'])):
            raise ValidationError('Нужны только уникальные теги')
        return data

    def create(self, validated_data):
        recipe = Recipe.objects.filter(
            name=self.validated_data['name'],
            text=self.validated_data['text'],
            cooking_time=self.validated_data['cooking_time'],
        ).exists()
        if recipe:
            raise ValidationError('Рецепт уже существует')
        with transaction.atomic():
            obj = Recipe(
                name=self.validated_data['name'],
                image=self.convert_base64_to_image(),
                text=self.validated_data['text'],
                cooking_time=self.validated_data['cooking_time'],
                author=self.context['request'].user
            )
            obj.save()
            ingredients = [IngredientLink(
                ingredient=item['id'],
                recipe=obj,
                amount=item['amount']
            ) for item in self.validated_data['ingredients']]
            IngredientLink.objects.bulk_create(ingredients)
            obj.tags.set(self.validated_data['tags'])
            return obj

    def update(self, instance, validated_data):
        with transaction.atomic():
            instance.name = self.validated_data['name']
            instance.text = self.validated_data['text']
            instance.cooking_time = self.validated_data['cooking_time']
            if self.validated_data.get('image'):
                instance.image = self.convert_base64_to_image()
            instance.tags.set(self.validated_data['tags'])
            instance.save()
            for ingredient in IngredientLink.objects.filter(recipe=instance):
                ingredient.delete()
            ingredients = [IngredientLink(
                ingredient=item['id'],
                recipe=instance,
                amount=item['amount']
            ) for item in self.validated_data['ingredients']]
            IngredientLink.objects.bulk_create(ingredients)
            return instance
