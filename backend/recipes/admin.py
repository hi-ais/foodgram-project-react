from django.contrib import admin

from .models import (Tag, Ingredient, Recipe,
                     IngredientVolume, FavoriteRecipe,
                     ShoppingCard)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'count_favorites')
    list_filter = ('author', 'name', 'tags')

    def count_favorites(self,obj):
        return obj.favorite_recipe.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


admin.site.register(Tag)
admin.site.register(IngredientVolume)
admin.site.register(FavoriteRecipe)
admin.site.register(ShoppingCard)
