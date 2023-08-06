from datetime import datetime as dt

from django.apps import apps
from django.db.models import F, Sum

from foodgram.settings import DATE_TIME_FORMAT
from recipes.models import AmountIngredient


def recipe_ingredients_set(
    recipe, ingredients
):
    objs = []

    for ingredient, amount in ingredients.values():
        objs.append(
            AmountIngredient(
                recipe=recipe, ingredients=ingredient, amount=amount
            )
        )

    AmountIngredient.objects.bulk_create(objs)


def create_shoping_list(user):
    shopping_list = [
        f"Список покупок для:\n\n{user.first_name}\n"
        f"{dt.now().strftime(DATE_TIME_FORMAT)}\n"
    ]
    Ingredient = apps.get_model("recipes", "Ingredient")
    ingredients = (
        Ingredient.objects.filter(recipe__recipe__in_carts__user=user)
        .values("name", measurement=F("measurement_unit"))
        .annotate(amount=Sum("recipe__amount"))
    )
    ing_list = (
        f'{ing["name"]}: {ing["amount"]} {ing["measurement"]}'
        for ing in ingredients
    )
    shopping_list.extend(ing_list)

    shopping_list.append("\nПосчитано в Foodgram")
    return "\n".join(shopping_list)
