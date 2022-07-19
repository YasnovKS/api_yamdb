from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from users.models import User


class RegisterSerilizer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'username')
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=('username', 'email')
            )]
