from django.db import models


class Category(models.Model):
    name = models.CharField('категория', max_length=256, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name[:15]
