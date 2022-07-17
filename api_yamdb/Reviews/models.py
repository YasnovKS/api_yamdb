from django.db import models


class Category(models.Model):
    name = models.CharField('имя категории', max_length=256)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name[:15]
