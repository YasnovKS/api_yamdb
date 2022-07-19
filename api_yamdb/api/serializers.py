import datetime

from django.db.models import Avg
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from reviews.models import Category, Genre, GenreTitle, Title


class CategorySerializer(serializers.ModelSerializer):

    slug = serializers.SlugField(
        max_length=50,
        validators=[
            UniqueValidator(
                queryset=Category.objects.all(),
                message='Указанная категория уже есть в БД',
            )
        ],
    )

    class Meta:
        model = Category
        fields = (
            'name',
            'slug',
        )


class CategorySlugOnlySerializer(serializers.ModelSerializer):
    """
    Serializer where only Category slug should be passed for creation.
    """

    class Meta:
        model = Category
        fields = (
            'name',
            'slug',
        )
        read_only_fields = ('name',)


class GenreSerializer(serializers.ModelSerializer):

    slug = serializers.SlugField(
        max_length=50,
        validators=[
            UniqueValidator(
                queryset=Genre.objects.all(),
                message='Указанный жанр уже есть в БД',
            )
        ],
    )

    class Meta:
        model = Genre
        fields = (
            'name',
            'slug',
        )


class GenreSlugOnlySerializer(serializers.ModelSerializer):
    """
    Serializer where only Genre slug should be passed for creation.
    """

    class Meta:
        model = Genre
        fields = (
            'name',
            'slug',
        )
        read_only_fields = ('name',)


class TitleSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()
    genre = GenreSlugOnlySerializer(many=True)
    category = CategorySlugOnlySerializer()

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'description',
            'rating',
            'genre',
            'category',
        )

        # TODO: Can we also restrict by Category
        validators = [
            UniqueTogetherValidator(
                queryset=Title.objects.all(),
                fields=('name', 'year'),
                message='Такое произведение уже есть в БД',
            )
        ]

    def get_rating(self, obj):
        """
        Retrieves average score from reviews.
        avg aggregate returns float but per redoc, rating should be
        an integer. Thus, it is converted to int.
        """
        avg_rating, *_ = obj.reviews.aggregate(Avg('score')).values()
        rating = int(avg_rating) if avg_rating else 0
        return rating

    def validate_year(self, value):
        todays_year = datetime.date.today().year
        if value > todays_year:
            raise serializers.ValidationError(
                f'Год выпуска {value} не может быть больше '
                f'текущего {todays_year}'
            )
        return value

    def validate_category(self, value):
        """
        Checks if category exists in db
        """
        count = Category.objects.filter(**value).count()
        if count == 0:
            category_slug = value.get('slug')
            raise serializers.ValidationError(
                f'Категории {category_slug} не существует'
            )
        return value

    def validate_genre(self, value):
        """
        Checks if genre exists in db.
        """
        for genre in value:
            count = Genre.objects.filter(**genre).count()
            if count == 0:
                genre_slug = genre.get('slug')
                raise serializers.ValidationError(
                    f'Жанра {genre_slug} не существует'
                )
        return value

    def create(self, validated_data):
        genres = validated_data.pop('genre')
        category_data = validated_data.pop('category')
        category = Category.objects.get(**category_data)
        title = Title.objects.create(**validated_data, category=category)
        for genre in genres:
            current_genre = Genre.objects.get(**genre)
            GenreTitle.objects.create(genre=current_genre, title=title)
        return title

    def update(self, instance, validated_data):
        # popping values that will be processed separately
        genres = validated_data.pop('genre')
        category_data = validated_data.pop('category')
        category = Category.objects.get(**category_data)

        # setting new values to model instance
        for fieldname, value in validated_data.items():
            setattr(instance, fieldname, value)
        instance.category = category

        # delete all current genres-title entries and add new ones
        GenreTitle.objects.filter(title=instance).delete()
        for genre in genres:
            current_genre = Genre.objects.get(**genre)
            GenreTitle.objects.create(genre=current_genre, title=instance)

        # saving updates to db and return updated instance
        instance.save()
        return instance
