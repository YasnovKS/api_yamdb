from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets

from reviews.models import Title, Review
from api.serializers import (ReviewSerializer, CommentSerializer,
                             RegisterSerilizer)
from django.core.mail import send_mail
import uuid


class RegisterViewSet(mixins.CreateModelMixin,
                      viewsets.GenericViewSet):
    confirmation_code = str(uuid.uuid4())
    serializer_class = RegisterSerilizer

    def perform_create(self, serializer):
        serializer.save(confirmation_code=self.confirmation_code)
        send_mail(
            'E-mail verification',
            f'Your confirmation_code is {self.confirmation_code}',
            'register@yamdb.ru',
            [serializer.data['email']]
        )


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
