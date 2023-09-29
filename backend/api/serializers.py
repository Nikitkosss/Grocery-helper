from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.validators import UniqueTogetherValidator
from users.models import Subscribe, User

from backend.settings import MAX_VALUE, MIN_VALUE


class UsersSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name',
            'last_name', 'is_subscribed', 'password',
        )

    def create(self, validated_data):
        return User.objects.create_user(
            **validated_data
        )

    def get_is_subscribed(self, obj):
        if not self.context['request'].user.is_anonymous:
            return Subscribe.signed_user.filter(
                user=self.context['request'].user,
                author=obj
            ).exists()
        return False


class SubscribeSerializer(UsersSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UsersSerializer.Meta):
        fields = UsersSerializer.Meta.fields + ('recipes', 'recipes_count',)
        read_only_fields = ('email', 'username', 'last_name', 'first_name',)

    def get_recipes(self, obj):
        return Recipe.author.filter(author=obj)

    def get_recipes_count(self, obj):
        return Recipe.author.filter(author=obj).count


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('__all__',)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('author', 'name', 'image', 'cooking_time',)


class IngredientsInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id',)
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UsersSerializer(read_only=True)
    ingredients = IngredientsInRecipeSerializer(
        many=True,
        source='recipe',
    )
    is_favorited = serializers.SerializerMethodField(
        read_only=True,
    )
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited',
            'name', 'image', 'text', 'cooking_time',
            'is_in_shopping_cart',
        )

    def get_ingredients(self, obj):
        queryset = IngredientAmount.objects.filter(recipe=obj)
        return IngredientsInRecipeSerializer(queryset, many=True).data

    def get_is_cart(self, obj):
        if self.context['request'].user.is_authenticated:
            return ShoppingCart.recipe_shopping_cart.filter(
                user=self.context['request'].user, recipe=obj
            ).exists()
        return False

    def get_is_favorite(self, obj):
        if self.context['request'].user.is_authenticated:
            return obj.recipe_in_favorites.filter(
                user=self.context['request'].user, recipe=obj
            ).exists()
        return False


class CreateUpdateRecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(
        many=True,
        required=True,
    )
    tags = PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        required=True,
    )
    image = Base64ImageField(
        required=False,
        allow_null=True,
    )
    author = UsersSerializer(
        read_only=True,
    )
    cooking_time = serializers.IntegerField(
        required=True,
        min_value=MIN_VALUE,
        max_value=MAX_VALUE,
    )

    class Meta:
        model = Recipe
        fields = '__all__'

    def ingredient_create(recipe, ingredients):
        return IngredientAmount.objects.bulk_create([
            IngredientAmount(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount'],
            )
            for ingredient in ingredients
        ])

    def validate(self, obj):
        if not obj.get('ingredients'):
            raise serializers.ValidationError(
                'Добавьте хотя бы один ингредиент.'
            )
        ingredients_data = [
            value['id'] for value in obj.get('ingredients')
        ]
        if len(ingredients_data) != len(set(ingredients_data)):
            raise serializers.ValidationError(
                'Ингредиенты должны быть уникальными.'
            )
        if not obj.get('tags'):
            raise serializers.ValidationError(
                'Укажите хотябы один тег.'
            )
        if len(obj.get('tags')) != len(set(obj.get('tags'))):
            raise serializers.ValidationError(
                'Теги должны быть уникальны.'
            )
        return obj

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=author, **validated_data)
        for tag in tags:
            recipe.tags.add(tag)
        ingredients = validated_data.pop('ingredients')
        self.ingredient_create(recipe, ingredients)
        return recipe

    def update(self, recipe, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            recipe.ingredients.clear()
            self.ingredient_create(recipe, ingredients)
        if 'tags' in validated_data:
            tags_data = validated_data.pop('tags')
            recipe.tags.set(tags_data)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }).data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'
        validators = (
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в избранное.'
            )
        )


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = '__all__'


class IngredientAmountSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientAmount
        fields = '__all__'


class SetPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return validated_data
