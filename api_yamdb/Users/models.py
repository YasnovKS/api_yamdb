from django.db import models
from django.contrib.auth.models import AbstractUser

ROLES = (('user', 'Пользователь'),
         ('moderator', 'Модератор'),
         ('admin', 'Администратор')
         )


class User(AbstractUser):
    email = models.EmailField(unique=True)
    bio = models.TextField(max_length=500,
                           blank=True,
                           verbose_name='О себе',
                           )
    role = models.CharField(max_length=20,
                            choices=ROLES,
                            default='user',
                            verbose_name='Роль')
    USERNAME_FIELD = 'username'
