from django.core import validators
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.constraints import UniqueConstraint
from users.models import User

from backend.settings import MAX_VALUE, MIN_VALUE


class Tag(models.Model):
    name = models.CharField(
        verbose_name="Тэг",
        max_length=100,
        unique=True,
    )
    color = models.CharField(
        verbose_name="Цвет",
        max_length=100,
        unique=True,
        validators=(
            validators.RegexValidator(
                r'^#([A-Fa-f0-9]){3,6}$',
                message='Введите цвет в формате HEX'
            ),
        ),
    )
    slug = models.SlugField(
        verbose_name="Слаг тэга",
        max_length=100,
        unique=True,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name="Ингридиент",
        max_length=100,
    )
    measurement_unit = models.CharField(
        verbose_name="Единицы измерения",
        max_length=24,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}.'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name="Автор рецепта",
        related_name="recipe_author",
        on_delete=models.SET_NULL,
        null=True,
    )
    name = models.CharField(
        verbose_name="Название блюда",
        max_length=100,
    )
    image = models.ImageField(
        verbose_name="Изображение блюда",
        upload_to='static/',
        null=True,
        blank=True,
    )
    text = models.TextField(
        verbose_name="Описание блюда",
        max_length=256,
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[
            MinValueValidator(MIN_VALUE),
            MaxValueValidator(MAX_VALUE),
        ]
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name="Ингредиенты блюда",
        related_name="recipes",
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Тег",
        related_name="recipes",
    )

    pub_date = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True,
    )

    class Meta:
        ordering = ('pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.author.email}, {self.name}'


class IngredientAmount(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient',
        verbose_name='Ингредиент',

    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Рецепт',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(MIN_VALUE),
            MaxValueValidator(MAX_VALUE),
        ]
    )

    class Meta:
        ordering = ('ingredient',)
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='Уникальный ингредиент',
            ),
        ]

    def __str__(self):
        return str(self.ingredient)


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='users_favorites',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Избранный рецепт',
        related_name='recipe_in_favorites',
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='Уникальное избранное',
            ),
        ]

    def __str__(self):
        return str(self.user)


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Добавил в корзину',
        related_name='shopping_cart_owner',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт в корзине',
        related_name='recipe_shopping_cart',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            ),
        ]

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'
