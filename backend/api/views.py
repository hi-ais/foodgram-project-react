from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
#from rest_framework.exceptions import NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated

from api.serializers import (TagSerializer, IngredientSerializer,
                             FollowSerializer, RecipeSerializer,
                             ShowShortRecipesSerializer)
from api.pagination import LimitPageNumberPagination
from api.permission import IsAuthorOrReadOnlyPermission
from api.mixins import ListCreateDeleteViewSet
from recipes.models import (Tag, Ingredient, Recipe,
                            FavoriteRecipe, ShoppingCard)
from users.models import Follow

User = get_user_model()


class UserSubscribeViewSet(ListCreateDeleteViewSet):
    """Реализация подписки/отписки на/от другого
    пользователя: эндпоинт users/subscriptions."""
    #queryset = User.objects.all() не нужно
    serializer_class = FollowSerializer
    pagination_class = LimitPageNumberPagination
    permission_classes = [IsAuthenticated, ]

    def list(self, request):
        user = request.user
        queryset = Follow.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(pages, many=True,
                                      context={'request': request})
        return self.get_paginated_response(serializer.data)

    def create(self, request, user_id):
        user = request.user
        author = get_object_or_404(User, id=user_id)
        if user == author:
            return Response({
                'errors': 'Вы не можете подписаться на самого себя'
            }, status=status.HTTP_400_BAD_REQUEST)
        if Follow.objects.filter(user=user, author=author).exists():
            return Response({
                'errors': 'Вы уже подписаны на данного пользователя'
            }, status=status.HTTP_400_BAD_REQUEST)
        folowing = Follow.objects.create(user=user, author=author)
        serializer = FollowSerializer(folowing, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, user_id):
        user = request.user
        author = get_object_or_404(User, id=user_id)
        if user == author:
            return Response({
                'errors': 'Вы не можете отписаться от самого себя'
            }, status=status.HTTP_400_BAD_REQUEST)
        folowing = Follow.objects.filter(user=user, author=author)
        if folowing.exists():
            folowing.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({
                'errors': 'Вы уже отписались'
            }, status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitPageNumberPagination
    permission_classes = (IsAuthorOrReadOnlyPermission,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated, ])
    def favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            FavoriteRecipe.objects.create(user=user, recipe=recipe)
            serializer = ShowShortRecipesSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            fav = FavoriteRecipe.objects.filter(user=user, recipe=recipe)
            if fav.exists():
                fav.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        return None

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated, ])
    def shopping_card(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            ShoppingCard.objects.create(user=user, recipe=recipe)
            serializer = ShowShortRecipesSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            fav = ShoppingCard.objects.filter(user=user, recipe=recipe)
            if fav.exists():
                fav.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        return None

