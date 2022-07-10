from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer, UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Tag, Ingredient, Recipe, IngredientVolume,
                            FavoriteRecipe, ShoppingCard)
from users.models import Follow


User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    last_name = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

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


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj.id).exists()


class ShowShortRecipesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class FollowSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='authoe.first_name')
    last_name = serializers.ReadOnlyField(source="author.last_name")
    is_subscribe = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribe', 'recipes',
                  'recipes_count',)

    def get_is_subscribe(self, obj):
        return Follow.objects.filter(user=obj.user, author=obj.id).exists()

    def get_recipes(self, obj):
        author_recipes = Recipe.objects.filter(author=obj.author)
        return ShowShortRecipesSerializer(author_recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientVolume
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(source='ingredientamount_set',
                                             read_only=True, many=True)
    image = Base64ImageField()
    is_favorite = serializers.SerializerMethodField()
    is_in_shopping_card = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorite', 'is_in_shopping_card',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorite(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(user=user).exists()

    def get_is_in_shopping_card(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCard.objects.filter(user=user).exists()
