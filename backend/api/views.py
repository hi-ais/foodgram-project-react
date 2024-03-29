from django.conf import settings as set
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (FavoriteRecipe, Ingredient, IngredientVolume,
                            Recipe, ShoppingCard, Tag)
from users.models import Follow

from api.filters import IngredientSearchFilter, RecipeFilterBackend
from api.functions import del_obj, post_obj
from api.mixins import ListCreateDeleteViewSet
from api.pagination import LimitPageNumberPagination
from api.permission import IsAuthorOrReadOnlyPermission
from api.serializers import (FollowSerializer, IngredientSerializer,
                             RecipeSerializer, SubscribeSerializer,
                             TagSerializer)

User = get_user_model()


class UserSubscribeViewSet(ListCreateDeleteViewSet):
    """
    Реализация подписки/отписки на/от другого
    пользователя: эндпоинт users/<int:user_id>/subscribe/
    Вывод списка пользователей, на которых подписан
    пользователь: эндпоинт users/subscriptions/.
    """
    serializer_class = SubscribeSerializer
    pagination_class = LimitPageNumberPagination
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

    def list(self, request):
        user = request.user
        queryset = user.follower.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(pages, many=True,
                                      context={'request': request})
        return self.get_paginated_response(serializer.data)

    def create(self, request, user_id):
        data = {'user': request.user.id, 'author': user_id}
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        instance_serializer = FollowSerializer(instance)
        return Response(instance_serializer.data,
                        status=status.HTTP_201_CREATED)

    def destroy(self, request, user_id):
        user = request.user
        author = get_object_or_404(User, id=user_id)
        follow = get_object_or_404(
            Follow, user=user, author=author
        )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вывод списка тегов.
    Теги может создавать только админ.
    Эндпоинты: tags, tags/<int:tags_id>.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """"
    Вывод списка ингредиентов.
    Ингредиенты может создавать только админ.
    Эндпоинты: ingredients,
    ingredients/<int:ingredients_id>.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """"
    Вывод списка рецептов/ отельного рецепта -
    доступно всем пользователям.
    Авторизованным пользователям доступно:
    создание/редактирование/удаление рецепта,
    добавление/удаление рецепта в избранное,
    добавление/удаление рецепта в  список покупок,
    получние текстового файла со списком покупок.
    """
    serializer_class = RecipeSerializer
    pagination_class = LimitPageNumberPagination
    permission_classes = (IsAuthorOrReadOnlyPermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilterBackend

    def get_queryset(self):
        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited is not None and int(is_favorited) == 1:
            return Recipe.objects.filter(
                favorite_recipe__user=self.request.user)
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')
        if is_in_shopping_cart is not None and int(is_in_shopping_cart) == 1:
            return Recipe.objects.filter(cart__user=self.request.user)
        return Recipe.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=('post', 'delete',), detail=True,
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            return post_obj(FavoriteRecipe, request.user, pk)
        elif request.method == 'DELETE':
            return del_obj(FavoriteRecipe, request.user, pk)
        return None

    @action(methods=('post', 'delete',), detail=True,
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            return post_obj(ShoppingCard, request.user, pk)
        elif request.method == 'DELETE':
            return del_obj(ShoppingCard, request.user, pk)
        return None

    @action(methods=('get',), detail=False,
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = IngredientVolume.objects.filter(
            recipe__cart__user=user).values(
                'ingredient__name',
                'ingredient__measurement_unit').annotate(
                    total=Sum('amount'))
        my_shopping_list = 'Мой cписок покупок: \n'
        for item in ingredients:
            my_shopping_list += (
                f'{item["ingredient__name"]}-'
                f'{item["total"]} '
                f'{item["ingredient__measurement_unit"]}\n'
            )
        content_type = 'text/plain'
        response = HttpResponse(
            my_shopping_list, content_type=content_type)
        response[
            'Content-Disposition'] = f'attachment; filename={set.FILENAME}'
        return response
