# from backend.foodgram.recipes.models import IngredientRecipe
from webbrowser import get
from django.db.models.query import QuerySet
from .filter import RecipeFilter 
from recipes.models import IngredientRecipe
from recipes.models import Tag, Recipe, Ingredient, Follow, Favorite, Basket, User
from django.shortcuts import get_object_or_404
from .serializers import TagSerializer, RecipeSerializer, IngredientSerializer, RecipeListSerializer, FavoriteSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .mixins import ModelMixinSet
from .permissions import IsAdminUserOrReadOnly, OwnerOrReadOnly
from rest_framework.views import APIView
# from rest_framework.decorators import permission_classes
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from django.core.exceptions import PermissionDenied
from django.http import FileResponse
from django.http import HttpResponse
from rest_framework.pagination import PageNumberPagination
from recipes.pagination import CustomPagination
from django_filters.rest_framework import DjangoFilterBackend
from api.filter import IngredientFilter
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination



# User = get_user_model()



def is_in_shopping_cart(user, recipe):
    try:
        get_object_or_404(Basket, user=user, recipe=recipe)
        return True
    except:
        return False


def is_favorited(user, recipe):
    try:
        get_object_or_404(Favorite, user=user, recipe=recipe)
        return True
    except:
        return False

def is_subscribed(user, author):
    try:
        get_object_or_404(Follow, author=author, user=user)
        return True
    except:
        return False
    


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer
    # pagination_class = PageNumberPagination
    pagination_class = None


    


    def list(self, request):
        queryset = self.get_queryset()
        serializer = TagSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        tag = get_object_or_404(queryset, pk=pk)
        serializer = TagSerializer(tag)
        return Response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('id')
    serializer_class = RecipeSerializer
    permission_classes = (OwnerOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter



    # def get_queryset(self):
    #     # search_param = self.request.query_params
    #     # if search_param:
    #     #     queryset = Ingredient.objects.filter(name__istartswith=search_param[0])
    #     # else:
    #     #     queryset = Ingredient.objects.all()
    #     # return queryset

    #     return Recipe.objects.all().order_by('id')

    def list(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer_context = {'request': request}
        serializer = RecipeListSerializer(page, context=serializer_context, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = get_object_or_404(Recipe, pk=pk)
        serializer = RecipeListSerializer(queryset)
        return Response(serializer.data)

    def perform_create(self, serializer):

        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)


    def get_permissions(self):
        if self.action == 'retrieve':
            return (ReadOnly(),)
        return super().get_permissions()


    def delete(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)

        try:
            Recipe.objects.filter(pk=pk).delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({"errors": ("string")},
                             status=status.HTTP_400_BAD_REQUEST)


    @action(methods=['GET'], detail=False,
        permission_classes=[IsAuthenticated, ],
        url_path='download_shopping_cart')
    def download_basket(self, request):
        baskets = Basket.objects.filter(user=request.user)
        value = {}
        for basket in baskets:
            ingredients = IngredientRecipe.objects.filter(recipe=basket.recipe)
            for ingredient in ingredients:
                name = f'{ingredient.ingredient.name} ({ingredient.ingredient.measurement_unit})'
                tmp = value.get(name)
                if tmp is not None:

                    tmp = tmp + ingredient.amount
                else:
                    tmp = ingredient.amount

                value.update({name: tmp})
        output = ''
        for key, val in value.items():
            output += f'{key} - {val}\n'
        response = HttpResponse(output, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping-cart.txt"'
        return response
    



class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    #queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    # filter_backends = (DjangoFilterBackend,)
    # filterset_class = IngredientFilter



    def get_queryset(self):
        search_param = self.request.query_params.get('name')
        if search_param:
            queryset = Ingredient.objects.filter(name__istartswith=search_param[0])
        else:
            queryset = Ingredient.objects.all()
        return queryset
    


class FavoriteViewSet(APIView):
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination

    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        try:
            Favorite.objects.get(user=request.user, recipe=recipe)
            return Response({"fail": ("Already in favorite list")},
                             status=status.HTTP_400_BAD_REQUEST)
        except:
            Favorite.objects.create(user=request.user, recipe=recipe)
            serializer = FavoriteSerializer(recipe)
            return Response(serializer.data)

    
    def delete(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)

        try:
            get_object_or_404(Favorite, user=request.user, recipe=recipe)
            Favorite.objects.filter(user=request.user, recipe=recipe).delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({"errors": ("string")},
                             status=status.HTTP_400_BAD_REQUEST)


class BasketViewSet(APIView):
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination

    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        try:
            Basket.objects.get(user=request.user, recipe=recipe)
            return Response({"fail": ("Already in favorite list")},
                             status=status.HTTP_400_BAD_REQUEST)
        except:
            Basket.objects.create(user=request.user, recipe=recipe)
            serializer = FavoriteSerializer(recipe)
            return Response(serializer.data)

    
    def delete(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)

        try:
            get_object_or_404(Basket, user=request.user, recipe=recipe)
            Basket.objects.filter(user=request.user, recipe=recipe).delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({"errors": ("string")},
                             status=status.HTTP_400_BAD_REQUEST)

