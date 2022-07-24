from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from recipes.models import Recipe
from api.serializers import ShowShortRecipesSerializer


def post_obj(model, user, pk):
    if model.objects.filter(user=user, recipe__id=pk).exists():
        return Response({'errors': 'Этот рецепт уже добавлен!'},
                        status=status.HTTP_400_BAD_REQUEST)
    recipe = get_object_or_404(Recipe, id=pk)
    model.objects.create(user=user, recipe=recipe)
    serializer = ShowShortRecipesSerializer(recipe)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def del_obj(model, user, pk):
    recipe = model.objects.filter(user=user, recipe__id=pk)
    if recipe.exists():
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response({'errors': 'Вы уже удалили рецепт'},
                    status=status.HTTP_400_BAD_REQUEST)
