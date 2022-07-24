from django.contrib import admin

from .models import (FavoriteRecipe, Ingredient, IngredientVolume, Recipe,
                     ShoppingCard, Tag)


class IngredientVolumeInline(admin.TabularInline):
    model = IngredientVolume


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'count_favorites')
    list_filter = ('author', 'name', 'tags')
    search_fields = ('name', 'ingredients__name',)
    inlines = [IngredientVolumeInline]

    def count_favorites(self, obj):
        return obj.favorite_recipe.count()


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)


@admin.register(IngredientVolume)
class IngredientVolumeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount',)


@admin.register(ShoppingCard)
class ShoppingCardAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
