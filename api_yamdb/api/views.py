from rest_framework import viewsets

from .mixins import ListCreateDestroyViewSet
from .serializers import CategorySerializer, GenreSerializer, TitleSerializer
from Reviews.models import Category, Genre, Title


class CategoryViewSet(ListCreateDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(ListCreateDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
