import datetime

from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from .validators import TitleUniqueTogetherValidator
from reviews.models import Category, Comment, Genre, GenreTitle, Review, Title
from users.models import User


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


class CategorySlugOnlySerializer(serializers.RelatedField):
    """
    Serializer where only Category slug should be passed for creation.
    """

    queryset = Category.objects.all()

    def to_representation(self, value):
        data = {
            'name': value.name,
            'slug': value.slug,
        }
        return data

    def to_internal_value(self, data):
        value = {'slug': data}
        return value


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


class GenreSlugOnlySerializer(serializers.RelatedField):
    """
    Serializer where only Genre slug should be passed for creation.
    """

    queryset = Genre.objects.all()

    def to_representation(self, value):
        data = {
            'name': value.name,
            'slug': value.slug,
        }
        return data

    def to_internal_value(self, data):
        value = {'slug': data}
        return value


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
        validators = [
            TitleUniqueTogetherValidator(
                queryset=Title.objects.all(),
                fields=('name', 'year', 'category'),
                related_querysets={'category': Category.objects.all()},
                message='Такое произведение уже существует в БД',
            )
        ]

    def get_rating(self, obj):
        """
        Retrieves average score from reviews.
        avg aggregate returns float but per redoc, rating should be
        an integer. Thus, it is converted to int.
        """
        avg_rating, *_ = obj.reviews.aggregate(Avg('score')).values()
        rating = int(avg_rating) if avg_rating else None
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
        category_exists = Category.objects.filter(**value).exists()
        if not category_exists:
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
            genre_exists = Genre.objects.filter(**genre).exists()
            if not genre_exists:
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
        # before popping check that properties were specified,
        # otherwise exception will happen.
        genres = (
            validated_data.pop('genre') if 'genre' in validated_data else []
        )
        category_data = (
            validated_data.pop('category')
            if 'category' in validated_data
            else None
        )
        if category_data:
            category = Category.objects.get(**category_data)
            instance.category = category

        # setting new values to model instance
        for fieldname, value in validated_data.items():
            setattr(instance, fieldname, value)

        # delete all current genres-title entries and add new ones
        GenreTitle.objects.filter(title=instance).delete()
        for genre in genres:
            current_genre = Genre.objects.get(**genre)
            GenreTitle.objects.create(genre=current_genre, title=instance)

        # saving updates to db and return updated instance
        instance.save()
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username')
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(), fields=('username', 'email')
            )
        ]

    def validate_username(self, value):
        if value == "me":
            raise serializers.ValidationError(
                "You can't use 'me'" " as your username."
            )
        return value


class ObtainTokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')

    def validate(self, data):
        user = get_object_or_404(User, username=data.get('username'))
        if data.get('confirmation_code') != user.confirmation_code:
            raise serializers.ValidationError(
                'Incorrect "confirmation_code"' ' for user.'
            )
        return data


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    score = serializers.IntegerField(min_value=1, max_value=10)

    class Meta:
        model = Review
        fields = ['id', 'text', 'author', 'score', 'pub_date']
        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(), fields=['author', 'title']
            )
        ]


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'pub_date']
