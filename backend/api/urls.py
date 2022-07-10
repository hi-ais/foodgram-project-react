from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (TagViewSet, IngredientViewSet, UserSubscribeViewSet,RecipeViewSet,
                       RecipeList)

app_name = 'api'

router = DefaultRouter()
router.register(r'tags', TagViewSet, basename='api_tags')
router.register(r'ingredients', IngredientViewSet, basename='api_ingredients')
router.register(r'recipes', RecipeViewSet, basename='api_recipes')


urlpatterns = [
    path('users/<int:user_id>/subscribe/', UserSubscribeViewSet.as_view(
        {'post': 'create', 'delete': 'destroy'}), name='subscribe'
    ),
    path('users/subscriptions/', UserSubscribeViewSet.as_view(
        {'get': 'list'}), name='subscriptions'
    ),
    #path('recipes/', RecipeList.as_view()),
    #path('recipes/<int:pk>/', RecipeList.as_view()),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),

]
