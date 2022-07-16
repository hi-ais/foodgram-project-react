from django.http import HttpResponse
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from api.serializers import (TagSerializer, IngredientSerializer,
                             FollowSerializer, RecipeSerializer,
                             ShowShortRecipesSerializer)
from api.pagination import LimitPageNumberPagination
from api.permission import IsAuthorOrReadOnlyPermission
from api.mixins import ListCreateDeleteViewSet
from api.filters import RecipeFilterBackend
from api.functions import post_obj, del_obj
from recipes.models import (Tag, Ingredient, Recipe, FavoriteRecipe,
                            ShoppingCard, IngredientVolume)
from users.models import Follow

User = get_user_model()


class UserSubscribeViewSet(ListCreateDeleteViewSet):
    """
    Реализация подписки/отписки на/от другого
    пользователя: эндпоинт users/<int:user_id>/subscribe/
    Вывод списка пользователей, на которых подписан
    пользователь: эндпоинт users/subscriptions/.
    """
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
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


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
    queryset = Recipe.objects.all()
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

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated, ])
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            return post_obj(FavoriteRecipe, request.user, pk)
        elif request.method == 'DELETE':
            return del_obj(FavoriteRecipe, request.user, pk)
        return None

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated, ])
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            return post_obj(ShoppingCard, request.user, pk)
        elif request.method == 'DELETE':
            return del_obj(ShoppingCard, request.user, pk)
        return None

    @action(methods=['get'], detail=False,
            permission_classes=[IsAuthenticated, ])
    def download_shopping_cart(self, request):
        user = request.user
        in_basket = user.cart_owner.all()
        buying_list = {}
        for item in in_basket:
            recipe = item.recipe
            ingredients_in_recipe = IngredientVolume.objects.filter(
                                    recipe=recipe)
            for item in ingredients_in_recipe:
                amount = item.amount
                name = item.ingredient.name
                measurement_unit = item.ingredient.measurement_unit
                if name not in buying_list:
                    buying_list[name] = {
                        'amount': amount,
                        'measurement_unit': measurement_unit
                        }
                else:
                    buying_list[name]['amount'] = (
                        buying_list[name]['amount'] + amount
                    )
        shopping_list = []
        for item in buying_list:
            shopping_list.append(
             f'{item} - {buying_list[item]["amount"]} '
             f'{buying_list[item]["measurement_unit"]}\n'
            )
        response = HttpResponse(shopping_list, content_type='text/plain')
        filename = 'shopping_list.txt'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return HttpResponse(shopping_list, content_type='text/plain')
