from import_export import resources

from recipes.models import Ingredient


class IngredientResources(resources.ModelResource):
    class Meta:
        model = Ingredient
