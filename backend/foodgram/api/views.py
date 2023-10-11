from djoser.views import TokenCreateView
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.serializers import (UserSerializer, UserSetPasswordSerializer,
                             TagSerializer, IngredientSerializer,
                             SubscribeSerializer)
from recipes.models import Tag, Ingredient
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
