from django.urls import include, path
from .views import  UsersViewSet, APIDeleteToken, UpdatePassword, UserFollowingViewSet, CustomObtainAuthToken
from rest_framework.routers import SimpleRouter
from rest_framework.authtoken import views

router_v1 = SimpleRouter()

router_v1.register(
    r'',
    UsersViewSet, basename='users'
)

urlpatterns = [
    #path('auth/token/', APIGetToken.as_view(), name='get_token'),
    path('<int:pk>/subscribe/', UserFollowingViewSet.as_view()), 
    # path('subscriptions/',  APIDeleteToken.as_view())
    path('set_password/',  UpdatePassword.as_view()),
    path('', include(router_v1.urls)),
    path('token/login/', CustomObtainAuthToken.as_view(), name='auth_token'),  #obtain_auth_token
    path('token/logout/',  APIDeleteToken.as_view())
    #path('<int:id>/subscribe/', UserFollowingViewSet.as_view())

    #path('api-token-auth/', views.obtain_auth_token, name='auth_token'),
]
