from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Ingredient, IngredientVolume, Recipe, Tag
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.models import Follow
from django.conf import settings

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    last_name = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password',)


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed',
        read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed',)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()


class ShowShortRecipesSerializer(serializers.ModelSerializer):
    """Укороченная версия рецепта."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)
        read_only_fields = ('id', 'name', 'image', 'cooking_time',)


class FollowSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source="author.last_name")
    is_subscribe = serializers.SerializerMethodField(
        method_name='get_is_subscribe')
    recipes = serializers.SerializerMethodField(
        method_name='get_recipes')
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count')

    class Meta:
        model = Follow
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribe', 'recipes',
                  'recipes_count',)

    def get_is_subscribe(self, obj):
        return True

    def get_recipes(self, obj):
        author_recipes = Recipe.objects.filter(author=obj.author)
        return ShowShortRecipesSerializer(author_recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()


class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = ('user', 'author',)
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author'),
                message=('Вы уже подписаны на этого пользователя!')
            )
        ]

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        author = data['author']
        if request.user == author:
            raise serializers.ValidationError(
                'Вы не можете подписаться на себя!'
            )
        return data


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField()
    measurement_unit = serializers.ReadOnlyField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)
        validators = [
            UniqueTogetherValidator(
                queryset=Ingredient.objects.all(),
                fields=('name', 'measurement_unit',))]


class IngredientForRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True
    )

    class Meta:
        model = IngredientVolume
        fields = ('id', 'name', 'amount', 'measurement_unit',)


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientForRecipeSerializer(source='ingredientvolume_set',
                                                many=True, read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time',)

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Нужен хоть один ингридиент для рецепта'})
        ingredient_list = []
        for item in ingredients:
            ingredient = get_object_or_404(Ingredient,
                                           id=item['id'])
            if ingredient in ingredient_list:
                raise serializers.ValidationError('Ингредиенты должны '
                                                  'быть уникальными')
            ingredient_list.append(ingredient)
            if int(item['amount']) < settings.AMOUNT:
                raise serializers.ValidationError({
                    'ingredients': ('Убедитесь, что значение количества '
                                    'ингредиента больше 1')
                })
        data['ingredients'] = ingredients
        return data

    def validate_cooking_time(self, value):
        if value < settings.COOKING_TIME:
            raise serializers.ValidationError({
                'cooking_time': ('Время приготовления не может быть'
                                 'меньше минуты')
            })
        return value

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(favorite_recipe__user=user,
                                     id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(cart__user=user, id=obj.id).exists()

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            IngredientVolume.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = self.initial_data.get('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = self.initial_data.get('tags')
        recipe_update = super().update(instance, validated_data)
        IngredientVolume.objects.filter(recipe=instance).all().delete()
        recipe_update.tags.set(tags)
        self.create_ingredients(ingredients, recipe_update)
        recipe_update.save()
        return recipe_update
