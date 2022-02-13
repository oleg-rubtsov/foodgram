from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    SAFE_METHODS, AllowAny, BasePermission, IsAuthenticated)
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import (Basket, Favorite, Ingredient, IngredientRecipe,
                            Recipe, Tag)

from .filter import IngredientSearchFilter, RecipeFilter
from .permissions import OwnerOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeListSerializer, RecipeSerializer,
                          TagSerializer)


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-pub_date')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        return RecipeSerializer

    def perform_create(self, serializer):

        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [ReadOnly]
        elif self.action == 'destroy' or self.action == 'update':
            permission_classes = [OwnerOrReadOnly]
        else:
            permission_classes = [IsAuthenticated]
        # else:
        #     permission_classes = [IsAdminUserOrReadOnly]
        return [permission() for permission in permission_classes]

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
        recipes = [basket.recipe for basket in baskets]
        ingredient_recipe_objects = IngredientRecipe.objects.filter(
            recipe__in=recipes
        )
        value = {}
        for ingredient_r_o in ingredient_recipe_objects:
            name = (
                f'{ingredient_r_o.ingredient.name} '
                f'({ingredient_r_o.ingredient.measurement_unit})'
            )
            tmp = value.get(name)
            if tmp is not None:
                tmp = tmp + ingredient_r_o.amount
            else:
                tmp = ingredient_r_o.amount
            value.update({name: tmp})
        output = ''
        for key, val in value.items():
            output += f'{key} - {val}\n'
        response = HttpResponse(output, content_type='text/plain')
        response['Content-Disposition'] = \
            'attachment; filename="shopping-cart.txt"'
        return response


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    filter_backends = [IngredientSearchFilter]
    search_fields = ('^name',)
    pagination_class = None


class FavoriteViewSet(APIView):
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination

    def get(self, request, pk):
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

    def get(self, request, pk):
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
