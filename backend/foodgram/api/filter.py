
from recipes.models import Recipe
from recipes.models import Ingredient
from rest_framework.filters import SearchFilter
from rest_framework import filters
from django_filters import rest_framework as filters


class IngredientFilter(SearchFilter):
    def get_search_fields(self, view, request):
        fields = super(IngredientFilter, self).get_search_fields(view, request)
        if 'name' in fields:
            fields['name'] = 'search'
        return fields


class RecipeFilter(filters.FilterSet):
    text = filters.CharFilter()

    class Meta:
        model = Recipe
        fields = ['text']

class IngredientFilter(filters.FilterSet):
    measurement_unit = filters.CharFilter()

    class Meta:
        model = Ingredient
        fields = ['measurement_unit']