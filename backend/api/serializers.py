import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField, SlugRelatedField
from users.models import Subscribe, User

from backend.settings import MAX_VALUE, MIN_VALUE


class Base64ImageFieldSerializer(serializers.ImageField):
    """Сериализатор для декодирования картинки.
       Декодирует строку base64."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UsersSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name',
            'last_name', 'is_subscribed', 'password',
        )

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create_user(
            **validated_data
        )
        if password:
            user.set_password(password)
        user.save()
        return user

    def get_is_subscribed(self, obj):
        if self.context['request'].user.is_authenticated:
            return Subscribe.objects.filter(
                author=obj
            ).exists()
        return False


class SubscribeSerializer(UsersSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UsersSerializer.Meta):
        fields = UsersSerializer.Meta.fields + ('recipes', 'recipes_count',)
        read_only_fields = ('email', 'username', 'last_name', 'first_name',)

    def get_is_subscribed(self, obj):
        request = self.context['request']
        if request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(author=obj).exists()

    def get_recipes(self, obj):
        request = self.context['request']
        limit_recipes = request.query_params.get('recipes_limit')
        if limit_recipes is not None:
            recipes = Recipe.objects.all()[:(int(limit_recipes))]
        else:
            recipes = Recipe.objects.all()
        return RecipeSerializer(
            recipes,
            many=True,
            context={'request': request}
        ).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('__all__',)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('__all__',)


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
    is_cart = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_cart(self, obj):
        if self.context['request'].user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=self.context['request'].user, recipe=obj
            ).exists()
        return False

    def get_is_favorited(self, obj):
        if self.context['request'].user.is_authenticated:
            return Favorite.objects.filter(
                user=self.context['request'].user, recipe=obj
            ).exists()
        return False


class CreateUpdateRecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientsInRecipeSerializer(
        many=True,
    )
    tags = PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    image = Base64ImageFieldSerializer(
        required=False,
        allow_null=True,
    )
    author = SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    cooking_time = serializers.IntegerField(
        required=True,
        min_value=MIN_VALUE,
        max_value=MAX_VALUE,
    )

    class Meta:
        model = Recipe
        fields = '__all__'

    def ingredient_create(self, recipe, ingredients):
        return IngredientAmount.objects.bulk_create([
            IngredientAmount(
                ingredient=ingredient.get('id'),
                recipe=recipe,
                amount=ingredient.get('amount')
            )
            for ingredient in ingredients
        ])

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.ingredient_create(ingredients, recipe)
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

    def validate(self, data):
        user = self.context['request'].user
        recipe = data['recipe']
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                {'errors': 'Рецепт уже добавлен!'})
        return data

    def to_representation(self, instance):
        return RecipeSerializer(
            instance.recipe,
            context={'request': self.context['request']}).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = '__all__'

    def validate(self, data):
        user = self.context['request'].user
        recipe = data['recipe']
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                {'errors': 'Рецепт уже добавлен в список покупок!'})
        return data

    def to_representation(self, instance):
        return RecipeSerializer(
            instance.recipe,
            context={'request': self.context['request']}).data


class IngredientAmountSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientAmount
        fields = '__all__'


class SubscribeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписки."""

    class Meta:
        model = Subscribe
        fields = ('user', 'author')

    def validate(self, data):
        user = self.context['request'].user
        author = data['author']
        if user == author:
            raise serializers.ValidationError({
                'errors': 'Нельзя подписаться на себя.'
            })
        if Subscribe.objects.filter(author=author).exists():
            raise serializers.ValidationError({
                'errors': 'Вы уже подписаны на этого автора.'
            })
        return data

    def to_representation(self, instance):
        return SubscribeSerializer(
            instance.author,
            context={'request': self.context['request']}
        ).data
