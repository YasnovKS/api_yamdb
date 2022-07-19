from django import views
from rest_framework import filters, mixins, viewsets
from .serializers import (RegisterSerilizer)
import uuid
from django.core.mail import send_mail


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
