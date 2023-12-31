from django.contrib import admin
from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
from import_export.admin import ImportExportModelAdmin


@admin.register(Ingredient)
class IngredientAdmin(ImportExportModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name', )
    search_fields = ('name', )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    list_filter = ('name', 'color',)


class RecipeIngredientInline(admin.TabularInline):
    model = IngredientAmount

    def get_min_num(self, request, obj=None, **kwargs):
        min_num = 10
        if obj:
            return min_num


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'in_favorites', )
    list_filter = ('name', 'author', 'tags', )
    search_fields = ('name', )
    inlines = (RecipeIngredientInline, )

    def in_favorites(self, obj):
        return obj.recipe_in_favorites.filter(recipe=obj).count()

    in_favorites.short_description = 'Добавлен в избранное'


@admin.register(IngredientAmount)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    list_editable = ('recipe', 'ingredient', 'amount')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe', )
    search_fields = ('user', 'recipe', )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe', )
    search_fields = ('user', 'recipe', )
