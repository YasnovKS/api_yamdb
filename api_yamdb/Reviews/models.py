from django.db import models


class Category(models.Model):
    name = models.CharField('имя категории', max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return self.name[:15]


class Genre(models.Model):
    name = models.CharField('имя жанра', max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return self.name[:15]
