import uuid

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .mixins import ListCreateDestroyViewSet
from .permissions import IsAdminPermission, IsProfileOwnerPermission
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ObtainTokenSerializer,
                          RegisterSerializer, ReviewSerializer,
                          TitleSerializer, UsersAdminManageSerializer,
                          SelfProfileSerializer)
from reviews.models import Category, Genre, Review, Title
from users.models import User


class RegisterViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        try:
            user = User.objects.filter(username=request.data['username'],
                                       email=request.data['email'])[0]
            send_mail(
                'E-mail verification',
                f'Your confirmation_code is {user.confirmation_code}',
                'register@yamdb.ru',
                [request.data['email']],
            )
            return Response(request.data, status=status.HTTP_200_OK)
        except Exception:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK,
                            headers=headers)

    def perform_create(self, serializer):
        confirmation_code = str(uuid.uuid4())
        serializer.save(confirmation_code=confirmation_code)
        send_mail(
            'E-mail verification',
            f'Your confirmation_code is {confirmation_code}',
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
        return Response({'token': str(token)},
                        status=status.HTTP_200_OK)


class UsersAdminManageViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersAdminManageSerializer
    lookup_field = 'username'
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticated, IsAdminPermission)

    def perform_create(self, serializer):
        confirmation_code = str(uuid.uuid4())
        serializer.save(confirmation_code=confirmation_code)

    @action(methods=['get', 'patch'], detail=False,
            permission_classes=[IsAuthenticated,
            IsProfileOwnerPermission, IsAdminPermission]
            )
    def me(self, request):
        profile = User.objects.get(pk=request.user.id)
        if request.method == "GET":
            serializer = SelfProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = SelfProfileSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class CategoryViewSet(ListCreateDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    pagination_class = PageNumberPagination


class GenreViewSet(ListCreateDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    pagination_class = PageNumberPagination


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = (
        'category__slug',
        'genre__slug',
        'name',
        'year',
    )
    pagination_class = PageNumberPagination


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = []

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(title=title, author=self.request.user)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = []

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        serializer.save(review=review, author=self.request.user)

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all()
