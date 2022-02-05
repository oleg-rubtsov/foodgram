from django_filters import rest_framework as filters
from django_filters.widgets import BooleanWidget
from rest_framework import filters

from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(
        widget=BooleanWidget, method="filter_is_favorited"
    )
    is_in_shopping_cart = filters.BooleanFilter(
        widget=BooleanWidget, method="filter_is_in_shopping_cart"
    )
    tags = filters.AllValuesMultipleFilter(field_name='tag__slug')
    author = filters.AllValuesMultipleFilter(field_name='author__id')

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(favorites__user=user)
        return queryset  # Recipe.objects.exclude(favorites__user=user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(in_basket__user=user)
        return queryset

    class Meta:
        model = Recipe
        fields = ['tags', 'is_favorited', 'is_in_shopping_cart', 'author']
