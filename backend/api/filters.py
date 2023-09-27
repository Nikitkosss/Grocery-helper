from django_filters.rest_framework import FilterSet, filters
from recipes.models import Ingredient, Recipe, Tag
from users.models import User


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )
    is_favorite = filters.BooleanFilter(method='get_is_favorite')
    is_cart = filters.BooleanFilter(
        method='get_is_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorite', 'is_cart')

    def get_is_favorite(self, queryset, name, value):
        if value:
            return queryset.filter(recipe_in_favorites__user=self.request.user)
        return queryset

    def get_is_cart(self, queryset, name, value):
        if value:
            return queryset.filter(item_in_carts__user=self.request.user)
        return queryset
