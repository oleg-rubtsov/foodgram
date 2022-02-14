from django.contrib import admin

from .models import (Basket, Favorite, Follow, Ingredient, IngredientRecipe,
                     Recipe, Tag, User)


class TagAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "color", "slug")
    search_fields = ("name",)
    empty_value_display = "-пусто-"


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "pk", "name", "image", "text", "author",
        "cooking_time", "get_ingredients", "get_tags",
        "pub_date", "get_favorite_count"
    )
    list_filter = ("author", "name", "tags")
    search_fields = ("name",)
    empty_value_display = "-пусто-"
    inlines = [IngredientRecipeInline]


class IngredientAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "measurement_unit")
    search_fields = ("name",)
    empty_value_display = "-пусто-"


class RecipeInline(admin.TabularInline):
    model = Recipe


class BasketInline(admin.StackedInline):
    model = Basket


class FavoriteInline(admin.StackedInline):
    model = Favorite


class FollowInline(admin.StackedInline):
    model = Follow
    fk_name = 'user'


class UserAdmin(admin.ModelAdmin):
    list_display = (
        "pk", "first_name", "last_name",
        "email", "username", "password",
        "get_favorite_count",
        "get_follow_count",
        "get_basket_count",
        "is_active"
    )
    list_filter = ('email', 'username')
    search_fields = ("first_name",)
    empty_value_display = "-пусто-"
    inlines = [BasketInline, FavoriteInline, FollowInline]


admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(User, UserAdmin)
