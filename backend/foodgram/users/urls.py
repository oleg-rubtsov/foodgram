from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import UpdatePassword, UserFollowingViewSet, UsersViewSet

router_v1 = SimpleRouter()

router_v1.register(
    r'',
    UsersViewSet, basename='users'
)

urlpatterns = [
    path('', include('djoser.urls.authtoken')),
    path('<int:pk>/subscribe/', UserFollowingViewSet.as_view()),
    path('set_password/',  UpdatePassword.as_view()),
    path('', include(router_v1.urls)),
]
