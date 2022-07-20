from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import User


class Category(models.Model):
    name = models.CharField('имя категории', max_length=256)
    slug = models.SlugField(max_length=50)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('slug',), name='category')
        ]
        ordering = [
            'slug',
        ]

    def __str__(self):
        return self.name[:15]


class Genre(models.Model):
    name = models.CharField('имя жанра', max_length=256)
    slug = models.SlugField(max_length=50)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('slug',), name='unique_genre')
        ]
        ordering = [
            'slug',
        ]

    def __str__(self):
        return self.name[:15]


class Title(models.Model):
    name = models.CharField('название', max_length=256)
    year = models.PositiveIntegerField('год выпуска')
    description = models.TextField('описание', blank=True, default='')
    genre = models.ManyToManyField(Genre, through='GenreTitle')
    category = models.ForeignKey(
        Category,
        related_name='titles',
        on_delete=models.SET_NULL,
        null=True,
    )

    class Meta:
        ordering = [
            '-year',
        ]

    def __str__(self):
        return self.name[:15]


class GenreTitle(models.Model):
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
    )
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.genre} {self.title}'


class Review(models.Model):
    text = models.TextField('текст отзыва')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews'
    )
    score = models.PositiveSmallIntegerField(
        'оценка', validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    pub_date = models.DateTimeField('дата', auto_now_add=True)
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews'
    )

    class Meta:
        ordering = [
            'pub_date',
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'], name='unique_review'
            )
        ]

    def __str__(self):
        return f'{self.title} {self.text[:15]}'


class Comment(models.Model):
    text = models.TextField('комментарий')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments'
    )
    pub_date = models.DateTimeField('дата', auto_now_add=True)
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments'
    )

    class Meta:
        ordering = [
            'pub_date',
        ]

    def __str__(self):
        return f'{self.review} {self.text[:15]}'
