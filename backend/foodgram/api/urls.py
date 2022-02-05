from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (BasketViewSet, FavoriteViewSet, IngredientViewSet,
                    RecipeViewSet, TagViewSet)

router_v1 = SimpleRouter()

router_v1.register(
    r'tags',
    TagViewSet,
    basename='tags'
)

router_v1.register(
    r'recipes',
    RecipeViewSet,
    basename='recipes'
)

router_v1.register(
    r'ingredients',
    IngredientViewSet,
    basename='ingredients'
)


urlpatterns = [
    path('recipes/<int:pk>/favorite/', FavoriteViewSet.as_view()),
    path('recipes/<int:pk>/shopping_cart/', BasketViewSet.as_view()),
    path('', include(router_v1.urls)),
    path('users/', include('users.urls')),
    path('auth/', include('users.urls'))
]
