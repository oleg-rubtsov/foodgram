# from backend.foodgram.recipes.models import IngredientRecipe
from webbrowser import get
from django.db.models.query import QuerySet
from recipes.models import IngredientRecipe
from recipes.models import Tag, Recipe, Ingredient, Follow, Favorite, Basket
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



User = get_user_model()



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
    permission_classes = (AllowAny,)

    def list(self, request):
        queryset = Tag.objects.all()
        serializer = TagSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Tag.objects.all()
        tag = get_object_or_404(queryset, pk=pk)
        serializer = TagSerializer(tag)
        return Response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    # permission_classes = (OwnerOrReadOnly,)
    # throttle_classes = (AnonRateThrottle,)


    # @action(methods=['PUT'], detail=False,
    #         permission_classes=[IsAuthenticated, ])
    # def recipe_update(self, request, pk):
    #     queryset = get_object_or_404(Recipe, pk=pk)
    #     IngredientRecipe.objects.filter(recipe=queryset).delete()
    #     return self.perform_update(queryset)
    

    def list(self, request):
        queryset = Recipe.objects.all()
        serializer = RecipeListSerializer(queryset, many=True)
        my_data = serializer.data
        for item in my_data:
            author = User.objects.get(username=item['author']['username'])
            recipe = get_object_or_404(Recipe, id=item['id'])
            item['author']['is_subscribed'] = is_subscribed(request.user, author)
            item['is_in_shopping_cart'] = is_in_shopping_cart(request.user, recipe)
            item['is_favorited'] = is_favorited(request.user, recipe)

        return Response(my_data)

    def retrieve(self, request, pk=None):
        queryset = get_object_or_404(Recipe, pk=pk)
        # ingredient = get_object_or_404(queryset, pk=pk)
        serializer = RecipeListSerializer(queryset)
        my_data = serializer.data
        author = User.objects.get(username=my_data['author']['username'])
        recipe = get_object_or_404(Recipe, id=my_data['id'])
        my_data['author']['is_subscribed'] = is_subscribed(request.user, author)
        my_data['is_in_shopping_cart'] = is_in_shopping_cart(request.user, recipe)
        my_data['is_favorited'] = is_favorited(request.user, recipe)
        return Response(my_data)

    def perform_create(self, serializer):

        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)
        # queryset = get_object_or_404(Recipe, pk=pk)
        #IngredientRecipe.objects.filter(recipe=queryset).delete()
        
        # tmp.ingredients.delete()
        # if serializer.instance.author != self.request.user:
        #     raise PermissionDenied('Изменение чужого контента запрещено!')
        # super(RecipeViewSet, self).perform_update(serializer)
        # queryset = get_object_or_404(Recipe, pk=pk)

        #serializer = RecipeSerializer(queryset)
        # serializer.is_valid()
        #return Response(serializer.data)
        # serializer.save(author=self.request.user)

    def get_permissions(self):
        if self.action == 'retrieve':
            return (ReadOnly(),)
        return super().get_permissions()


    def delete(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)

        try:
            # IngredientRecipe.objects.filter(recipe=recipe).delete()
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
        # out = open('out.txt', 'w')
        # for key, val in value.items():
        #     out.write('{}:{}\n'.format(key, val))
        # out.close()
        # out = open('out.txt', 'r')
        output = ''
        for key, val in value.items():
            output += f'{key} - {val}\n'
        response = HttpResponse(output, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping-cart.txt"'
        return response
    



class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)

    def list(self, request):
        queryset = Ingredient.objects.all()
        serializer = IngredientSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Ingredient.objects.all()
        ingredient = get_object_or_404(queryset, pk=pk)
        serializer = IngredientSerializer(ingredient)
        return Response(serializer.data)



class FavoriteViewSet(APIView):
    permission_classes = (IsAuthenticated,)

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

