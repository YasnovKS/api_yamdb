from Reviews.management.base import ImportDataBaseCommand
from Reviews.models import Category, Genre, GenreTitle, Title
from Users.models import User


class Command(ImportDataBaseCommand):
    models = (
        Category,
        Genre,
        Title,
        GenreTitle,
        User,
    )
