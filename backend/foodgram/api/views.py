import io

from django.db.models import Q, Sum
from django.http import HttpResponse
from djoser.views import TokenCreateView
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.permissions import CheckPermissionsToUpdateAndDelete
from api.serializers import (UserSerializer, UserSetPasswordSerializer,
                             TagSerializer, IngredientSerializer,
                             SubscribeSerializer, RecipeSerializer,
                             FavoriteSerializer, ShoppingListSerializer,
                             PostUpdateRecipeSerializer)
from recipes.models import (Tag, Ingredient, Recipe, Favorite, ShoppingList)
from users.models import User, Subscription


class UserViewSet(ModelViewSet):
    model = User
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)
        return super().retrieve(request)

    @action(detail=False, methods=['GET'],
            permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        return Response(UserSerializer(request.user, context={
            'request': request}).data)

    @action(detail=False, methods=['POST'],
            permission_classes=[permissions.IsAuthenticated])
    def set_password(self, request):
        serializer = UserSetPasswordSerializer(data=request.data, context={
            'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'],
            permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        author_id = request.user.subscribes.all().values_list(
            'author_id', flat=True)
        self.queryset = User.objects.filter(id__in=author_id)
        self.serializer_class = SubscribeSerializer
        return super().list(request)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, pk):
        serializer = SubscribeSerializer(
            data={'id': pk},
            context={'request': request, 'method': request.method})
        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            subscribe = serializer.save()
            return Response(SubscribeSerializer(subscribe, context={
                'request': request,
                'recipes_limit': request.query_params.get('recipes_limit')
            }).data, status=status.HTTP_201_CREATED)
        Subscription.objects.get(user=request.user, author_id=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomTokenCreateView(TokenCreateView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            response.status_code = 201
        return response


class TagViewSet(ModelViewSet):
    model = Tag
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ModelViewSet):
    model = Ingredient
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None

    def list(self, request, *args, **kwargs):
        if request.query_params.get('name', None):
            self.queryset = self.queryset.filter(
                name__icontains=request.query_params['name'])
        return super().list(request)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticated,
                          CheckPermissionsToUpdateAndDelete]

    def list(self, request):
        if int(request.query_params.get('is_favorited', -1)) == 1:
            recipes_id = Favorite.objects.filter(
                user=request.user
            ).values_list('recipe_id', flat=True)
            self.queryset = self.queryset.filter(id__in=recipes_id)
        if int(request.query_params.get('is_in_shopping_cart', -1)) == 1:
            recipes_id = ShoppingList.objects.filter(
                user=request.user
            ).values_list('recipe_id', flat=True)
            self.queryset = self.queryset.filter(id__in=recipes_id)
        if request.query_params.get('author'):
            self.queryset = self.queryset.filter(
                author_id=int(request.query_params.get('author')))
        if request.query_params.get('tags'):
            filterr = Q()
            for tag in self.request.query_params.getlist('tags'):
                filterr |= Q(tags__slug__icontains=tag)
            self.queryset = self.queryset.filter(filterr)
        self.queryset = self.queryset.distinct()
        return super().list(request)

    def create(self, request):
        serializer = PostUpdateRecipeSerializer(data=request.data,
                                                context={'request': request})
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()
        return Response(RecipeSerializer(
            recipe, context={'request': request}
        ).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk, *args, **kwargs):
        obj = get_object_or_404(Recipe, pk=pk)
        self.check_object_permissions(request, obj)
        serializer = PostUpdateRecipeSerializer(obj, data=request.data,
                                                context={'request': request})
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()
        return Response(
            RecipeSerializer(recipe, context={'request': request}).data)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk):
        serializer = FavoriteSerializer(
            data={'id': pk},
            context={'request': request, 'method': request.method})
        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            favorite = serializer.save()
            return Response(FavoriteSerializer(favorite, context={
                'request': request,
            }).data, status=status.HTTP_201_CREATED)
        Favorite.objects.get(user=request.user, recipe_id=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk):
        serializer = ShoppingListSerializer(
            data={'id': pk},
            context={'request': request, 'method': request.method})
        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            shopping_list = serializer.save()
            return Response(ShoppingListSerializer(shopping_list, context={
                'request': request,
            }).data, status=status.HTTP_201_CREATED)
        ShoppingList.objects.get(user=request.user, recipe_id=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'],
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        recipes_id = ShoppingList.objects.filter(
            user=request.user).values_list('recipe__pk', flat=True)
        amts = Recipe.objects.filter(
            id__in=recipes_id
        ).annotate(
            quantity=Sum(
                'ingredients__link_of_ingredients__amount',
                filter=Q(
                    ingredients__link_of_ingredients__recipe_id__in=recipes_id
                )
            )
        ).distinct().values_list(
            'quantity', 'link_of_ingredients__ingredient__name',
            'link_of_ingredients__ingredient__measurement_unit'
        )
        listok = ''
        for i in range(len(amts)):
            listok += f'{amts[i][1]} ({amts[i][2]}) -- {amts[i][0]}\n'
        text = io.BytesIO()
        with io.TextIOWrapper(text, encoding="utf-8", write_through=True) as f:
            f.write(listok)
            response = HttpResponse(text.getvalue(), content_type="text/plain")
            response[
                "Content-Disposition"
            ] = "attachment; filename=spisok-pokupok.txt"
            return response
