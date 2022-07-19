from django.db import models

from users.models import User


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


class Title(models.Model):
    name = models.CharField('название', max_length=256)
    year = models.IntegerField('год выпуска')
    description = models.TextField('описание', null=True, blank=True)
    genre = models.ManyToManyField(Genre, through='GenreTitle')
    category = models.ForeignKey(
        Category,
        related_name='categories',
        on_delete=models.SET_NULL,
        null=True,
    )

    def __str__(self):
        return self.name[:15]


class GenreTitle(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.genre} {self.title}'


class Review(models.Model):
    text = models.TextField('текст отзыва')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.PositiveIntegerField('оценка')
    pub_date = models.DateTimeField('дата', auto_now_add=True)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    class Meta:
        ordering = ['pub_date', ]

    def __str__(self):
        return f'{self.title} {self.text[:15]}'


class Comment(models.Model):
    text = models.TextField('комментарий')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField('дата', auto_now_add=True)
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    class Meta:
        ordering = ['pub_date', ]

    def __str__(self):
        return f'{self.review} {self.text[:15]}'
