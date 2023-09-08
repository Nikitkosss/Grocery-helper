from django.core import validators
from django.db import models
from django.db.models.constraints import UniqueConstraint

from users.models import User


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

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name="Ингридиент",
        max_length=100,
    )
    units = models.CharField(
        verbose_name="Единицы измерения",
        max_length=24,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name="Автор рецепта",
        related_name="recipes",
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
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления в минутах',
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

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='Ингридиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='Рецепт',
    )
    amount = models.IntegerField(
        verbose_name="Количество",
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        constraints = [
            UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='Уникальный ингредиент',
            ),
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        related_name="favorites",
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Понравившиеся рецепты",
        related_name="in_favorites",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Избранное'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='Уникальное избранное',
            ),
        ]

    def __str__(self):
        return self.user


class Cart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="Владелец списка",
        related_name="carts",
        on_delete=models.CASCADE,
    )
    item = models.ForeignKey(
        Recipe,
        verbose_name="Рецепты в списке покупок",
        related_name="in_carts",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Список покупок'
        constraints = [
            UniqueConstraint(
                fields=['user', 'item'],
                name='Уникальный item списка покупок',
            )
        ]

    def __str__(self):
        return self.user
