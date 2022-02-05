from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from django.shortcuts import get_object_or_404
from .serializers import SubscriptionsSerializer, UsersSerializer, SignupSerializer, ChangePasswordSerializer, CustomAuthTokenSerializer # , UserFollowingSerializer, UserFollowersSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from django.core.exceptions import ObjectDoesNotExist
from api.permissions import IsAdminUserOrReadOnly
from django.contrib.auth import (
    login as django_login,
    logout as django_logout
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework import generics
from recipes.models import Follow, User
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework import exceptions
from users.utils import generate_access_token, generate_refresh_token
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.pagination import PageNumberPagination
import pdb




class APIDeleteToken(APIView):
    def post(self, request):
        return self.logout(request)

    def logout(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            return Response({"detail": ("Учетные данные не были предоставлены.")},
                        status=status.HTTP_401_UNAUTHORIZED)

        return Response({"success": ("Successfully logged out.")},
                        status=status.HTTP_200_OK)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UsersSerializer
    permission_classes = (IsAuthenticated, AllowAny,)

    @action(methods=['GET'], detail=False,
            permission_classes=[IsAuthenticated, ],
            url_path='me')
    def current_user(self, request):
        queryset = User.objects.all().order_by('id')
        serializer_context = {'request': request}
        user = get_object_or_404(queryset, username=request.user.username)
        serializer = UsersSerializer(user, context=serializer_context)
        return Response(serializer.data)


    @action(methods=['GET'], detail=False,
            permission_classes=[IsAuthenticated, ])
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer_context = {'request': request}
        serializer = SubscriptionsSerializer(page, context=serializer_context, many=True)
        return self.get_paginated_response(serializer.data)
    
    def get_permissions(self):
        if self.action == 'list' or self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def list(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer_context = {'request': request}
        serializer = UsersSerializer(page, context=serializer_context, many=True)
        return self.get_paginated_response(serializer.data)

    def create(self, request):
        if request.user.is_authenticated:
            return Response({"detail": ("Пользователь уже авторизован")},
                            status=status.HTTP_403_FORBIDDEN)
        else:
            serializer = SignupSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            data = serializer.data
            return Response(data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        if request.user.is_authenticated:
            queryset = User.objects.all().order_by('id')
            serializer_context = {'request': request}
            user = get_object_or_404(queryset, pk=pk)
            serializer = UsersSerializer(user, context=serializer_context)
            return Response(serializer.data)
        else:
            return Response({"detail": ("Учетные данные не были предоставлены.")},
                            status=status.HTTP_401_UNAUTHORIZED)
    
class UpdatePassword(APIView):
    permission_classes = (IsAuthenticated, )

    def get_object(self, queryset=None):
        return self.request.user

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            current_password = serializer.data.get("current_password")
            if not self.object.check_password(current_password):
                return Response({"current_password": ["Wrong password."]}, 
                                status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserFollowingViewSet(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        try:
            Follow.objects.get(user=request.user, author=author)
            return Response({"fail": ("You already subscribed")},
                             status=status.HTTP_400_BAD_REQUEST)
        except:
            if request.user != author:
                Follow.objects.create(user=request.user, author=author)
                serializer = UsersSerializer(author)
                my_data = serializer.data
                my_data['is_subscribed'] = True
                return Response(my_data)
            else:
                return Response({"fail": ("Fail subscribe.")},
                             status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        author = get_object_or_404(User, pk=pk)

        try:
            get_object_or_404(Follow, user=request.user, author=author)
            Follow.objects.filter(user=request.user, author=author).delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({"errors": ("string")},
                             status=status.HTTP_400_BAD_REQUEST)

        # queryset = User.objects.all()
        # user = get_object_or_404(queryset, username=request.user.username)
        # serializer = UsersSerializer(user)
        # return Response(serializer.data)
    
    # def delete(self, request, pk):
    #     permission_classes = (IsAuthenticated,)
    #     serializer_class = UserFollowersSerializer
    #     queryset = Follow.objects.all()
    #     return Response({"success": ("Successfully logged out.")},
    #                     status=status.HTTP_200_OK)


# class CustomObtainAuthToken(ObtainAuthToken):
    
#     def post(self, request):
#         serializer = CustomAuthTokenSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         email = serializer.validated_data['email']
#         tnp = User.objects.get(email=email)
#         token, created = Token.objects.get_or_create(user=tnp)
#         return Response({
#             'token': token.key,
#             # 'user_id': user.pk,
#             # 'email': user.email
#         })


class SubscriptionViewSet(APIView):
    pagination_class = None
    #queryset = User.objects.all()
    # serializer_class = UsersSerializer
    permission_classes = (IsAuthenticated)

    def get(self, request, format=None):
        usernames = [user.username for user in User.objects.all()]
        return Response(usernames)

    @action(methods=['GET'], detail=False,
            permission_classes=[IsAuthenticated, ],
            url_path='me')
    def subscriptions(self, request):
        followers = Follow.objects.filter(user=request.user)
        follower_list = []
        for item in followers:
            humon = item.author.username
            follower_list.append(humon)
        queryset = User.objects.filter(username__in=follower_list)
        # user = get_object_or_404(queryset, username=request.user.username)    
        #pdb.set_trace()
        page = self.paginate_queryset(queryset)
        serializer_context = {'request': request}
        serializer = UsersSerializer(page, context=serializer_context, many=True)

    # #     serializer = UsersSerializer(queryset, many=True)
    # #     my_data = serializer.data
    # #     for item in my_data:
    # #         item['is_subscribed'] = True
    # #     #my_data.save()
    # #   return self.get_paginated_response(my_data)


