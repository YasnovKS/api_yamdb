from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import ReviewViewSet, CommentViewSet, RegisterViewSet

app_name = 'api'


router = SimpleRouter()

router.register('auth/signup', RegisterViewSet, basename='register')
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews',
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments',
)

urlpatterns = [
    path('v1/', include(router.urls), name='api'),
]
