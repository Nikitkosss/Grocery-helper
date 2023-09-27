from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)
    email = models.EmailField(
        verbose_name='Почтовый адрес',
        max_length=254,
        unique=True,
    )
    username = models.CharField(
        verbose_name='Уникальный юзернейм',
        max_length=100,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=100,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=100,
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=128,
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        related_name='author',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='Подписчики',
        related_name='signed_user',
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ('-author_id',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author',),
                name='Уникальность подписки'
            ),
            models.CheckConstraint(
                check=models.Q(user=models.F('author')),
                name='Проверка самоподписки'
            )
        )

    def __str__(self):
        return f'{self.user.username} - {self.author.username}'
