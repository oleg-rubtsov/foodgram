from django.urls import include, path
from .views import  TagViewSet, RecipeViewSet, IngredientViewSet, FavoriteViewSet, BasketViewSet
from rest_framework.routers import SimpleRouter
from django.conf import settings
from django.conf.urls.static import static


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

# router = SimpleRouter()
# router.register('tags', TagViewSet, basename='tags')

urlpatterns = [
    path('recipes/<int:pk>/favorite/', FavoriteViewSet.as_view()),
    path('recipes/<int:pk>/shopping_cart/', BasketViewSet.as_view()),
    path('', include(router_v1.urls)),
    path('users/', include('users.urls')),
    path('auth/', include('users.urls'))
    #path('tags/', )
]
