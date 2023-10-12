from rest_framework.routers import DefaultRouter
from django.urls import path, include, re_path

from .views import (UserViewSet, CustomTokenCreateView, TagViewSet,
                    IngredientViewSet, RecipeViewSet)

app_name = 'api'

router_v2 = DefaultRouter()

router_v2.register('users', UserViewSet, basename='users')
router_v2.register('tags', TagViewSet, basename='tags')
router_v2.register('ingredients', IngredientViewSet, basename='ingredients')
router_v2.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router_v2.urls)),
    path('auth/token/login/', CustomTokenCreateView.as_view()),

    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
