from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from recipes.models import Tag, Ingredient, Recipe
from users.models import User, Subscription


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
            data['is_subscribed'] = 'qwe'
        else:
            data.pop('is_subscribed', None)
        return data


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
        if self.context.get('recipes_limit'):
            recipes = recipes[:int(self.context['recipes_limit'])]
        return SmallRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, instance):
        return instance.recipes.all().count()

    def validate(self, attrs):
        author = get_object_or_404(User, id=self.initial_data['id'])
        subscribe = Subscription.objects.filter(
            author=author, user=self.context['request'].user)
        if self.context['method'] == 'POST':
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
