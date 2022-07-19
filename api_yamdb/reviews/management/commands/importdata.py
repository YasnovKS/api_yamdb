from reviews.management.base import ImportDataBaseCommand
from reviews.models import Category, Genre, GenreTitle, Title
from users.models import User


class Command(ImportDataBaseCommand):
    models = (
        Category,
        Genre,
        Title,
        GenreTitle,
        User,
    )
