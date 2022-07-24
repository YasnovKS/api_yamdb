import uuid

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import  IsAuthenticatedOrReadOnly
from rest_framework import filters, mixins, status, views, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .filters import TitleFilter
from .mixins import ListCreateDestroyViewSet
from .permissions import IsAdminOrReadOnly
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ObtainTokenSerializer,
    ReadOnlyTitleSerializer,
    RegisterSerializer,
    ReviewSerializer,
    TitleSerializer,
)
from reviews.models import Category, Genre, Review, Title
from users.models import User
from api.permissions import AuthorPermission

class RegisterViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    confirmation_code = str(uuid.uuid4())
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_200_OK, headers=headers
        )

    def perform_create(self, serializer):
        serializer.save(confirmation_code=self.confirmation_code)
        send_mail(
            'E-mail verification',
            f'Your confirmation_code is {self.confirmation_code}',
            'register@yamdb.ru',
            [serializer.data['email']],
        )


class ObtainTokenView(views.APIView):
    def post(self, request):
        serializer = ObtainTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.data.get('username')
        user = get_object_or_404(User, username=username)
        token = RefreshToken.for_user(user).access_token
        return Response({'token': str(token)}, status=status.HTTP_200_OK)


class CategoryViewSet(ListCreateDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    permission_classes = (
        IsAdminOrReadOnly,
        permissions.IsAuthenticatedOrReadOnly,
    )
    filter_backends = (filters.SearchFilter,)
    search_fields = ('$name',)
    pagination_class = PageNumberPagination


class GenreViewSet(ListCreateDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    permission_classes = (
        IsAdminOrReadOnly,
        permissions.IsAuthenticatedOrReadOnly,
    )
    filter_backends = (filters.SearchFilter,)
    search_fields = ('$name',)
    pagination_class = PageNumberPagination


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    permission_classes = (
        IsAdminOrReadOnly,
        permissions.IsAuthenticatedOrReadOnly,
    )
    filter_backends = (DjangoFilterBackend,)
    filter_class = TitleFilter
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return TitleSerializer
        return ReadOnlyTitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (AuthorPermission, IsAuthenticatedOrReadOnly, )
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(title=title, author=self.request.user)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (AuthorPermission, IsAuthenticatedOrReadOnly, )
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        serializer.save(review=review, author=self.request.user)

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all()
