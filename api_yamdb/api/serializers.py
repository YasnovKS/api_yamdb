import datetime

from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

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


class ReadOnlyTitleSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

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

    def get_rating(self, obj):
        """
        Retrieves average score from reviews.
        avg aggregate returns float but per redoc, rating should be
        an integer. Thus, it is converted to int.
        """
        avg_rating, *_ = obj.reviews.aggregate(Avg('score')).values()
        rating = int(avg_rating) if avg_rating else None
        return rating


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        many=True, slug_field='slug', queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'description',
            'genre',
            'category',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Title.objects.all(),
                fields=('name', 'year', 'category'),
                message='Такое произведение уже существует в БД',
            )
        ]

    def validate_year(self, value):
        todays_year = datetime.date.today().year
        if value > todays_year:
            raise serializers.ValidationError(
                f'Год выпуска {value} не может быть больше '
                f'текущего {todays_year}'
            )
        return value

    def create(self, validated_data):
        genres = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)
        for genre in genres:
            GenreTitle.objects.create(genre=genre, title=title)
        return title

    def update(self, instance, validated_data):
        genres = (
            validated_data.pop('genre') if 'genre' in validated_data else []
        )

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

class CreateTitleDefault(object):
    def set_context(self, serializer_field):
        view = serializer_field.context['view']
        self.title = view.kwargs.get('title_id')

    def call(self):
        return self.title

class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    score = serializers.IntegerField(min_value=1, max_value=10)
    title = serializers.HiddenField(
        default=serializers.CreateOnlyDefault(CreateTitleDefault())
    )
    
    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'title')
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
        fields = ('id', 'text', 'author', 'pub_date')
