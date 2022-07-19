from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView

from .views import RegisterViewSet

router = routers.DefaultRouter()
router.register('auth/signup', RegisterViewSet, basename='register')

urlpatterns = [
    path('v1/', include(router.urls))
]
