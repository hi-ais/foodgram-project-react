from django.contrib import admin

from .models import (FavoriteRecipe, Ingredient, IngredientVolume, Recipe,
                     ShoppingCard, Tag)


class IngredientVolumeInline(admin.TabularInline):
    model = IngredientVolume


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'count_favorites',)
    list_filter = ('tags',)
    search_fields = ('name', 'author__username', 'author__email',)
    inlines = [IngredientVolumeInline]

    def count_favorites(self, obj):
        return obj.favorite_recipe.count()


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    list_filter = ('recipe__tags',)
    search_fields = ('user__username', 'user__email',
                     'recipe__name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)


@admin.register(IngredientVolume)
class IngredientVolumeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount',)
    search_fields = ('recipe__author__username',
                     'recipe__author__email',
                     'recipe__name',
                     'ingredient__name')
    list_filter = ('recipe__tags',)


@admin.register(ShoppingCard)
class ShoppingCardAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    search_fields = ('user__username',
                     'user__email',
                     'recipe__name')
    list_filter = ('recipe__tags',)
