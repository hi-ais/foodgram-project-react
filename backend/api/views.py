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
from recipes.models import (Tag, Ingredient, Recipe, FavoriteRecipe,
                            ShoppingCard, IngredientVolume)
from users.models import Follow

User = get_user_model()


class UserSubscribeViewSet(ListCreateDeleteViewSet):
    """Реализация подписки/отписки на/от другого
    пользователя: эндпоинт users/subscriptions."""
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
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitPageNumberPagination
    permission_classes = (IsAuthorOrReadOnlyPermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('tags',) 

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

    @action(methods=['get'], detail=False,
            permission_classes=[IsAuthenticated, ])
    def download_shopping_cart(self, request):
        user = request.user
        in_basket = user.card_owner.all()
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