from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Адрес электронной почты',
        help_text='Введите свой адрес электронной почты',
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Имя пользователя',
        help_text='Введите свое имя пользователя',
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
        help_text='Введите имя',
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
        help_text='Введие Фамилию',
    )
    password = models.CharField(
        max_length=150,
        verbose_name='Пароль',
        help_text='Введите пароль',
    )

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribes',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name="unique_subscription"
            ),
        ]

    def __str__(self):
        return f'Подписка {self.user.username} на {self.author.username}'
