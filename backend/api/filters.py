from django_filters.rest_framework import FilterSet, filters
from recipes.models import Ingredient, Recipe
from users.models import User


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


IN_NOT_IN = (
    (0, 'Not_In'),
    (1, 'In'),
)


class RecipeFilter(FilterSet):

    author = filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )
    is_in_shopping_cart = filters.ChoiceFilter(
        choices=IN_NOT_IN, method='get_is_in'
    )
    is_favorited = filters.ChoiceFilter(
        choices=IN_NOT_IN,
        method='get_is_in'
    )
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        label='Ссылка'
    )

    def get_is_in(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if value == '1':
                if name == 'is_favorited':
                    queryset = queryset.filter(recipe_in_favorites__user=user)
                if name == 'is_in_shopping_cart':
                    queryset = queryset.filter(
                        recipe_recipe_shopping_cart__user=user
                    )
        return queryset

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']
