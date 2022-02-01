from django.contrib import admin

from .models import Tag, Recipe, Ingredient, IngredientRecipe, Follow, Favorite, Basket, User #  TagRecipe,


class TagAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "color", "slug")
    search_fields = ("name",)
    empty_value_display = "-пусто-"


# class TagRecipeAdmin(admin.ModelAdmin):
#     list_display = ("pk", "tag", "recipe")
#     search_fields = ("recipe",)
#     empty_value_display = "-пусто-"


class RecipeAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "image", "text", "author", "cooking_time", "get_ingredients", "get_tags") # , ,, 
    search_fields = ("name",)
    empty_value_display = "-пусто-"


class IngredientAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "measurement_unit")
    search_fields = ("name",)
    empty_value_display = "-пусто-"


class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ("pk", "ingredient", "recipe", "amount")
    search_fields = ("recipe",)
    empty_value_display = "-пусто-"



class FollowAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "author")
    search_fields = ("name",)
    empty_value_display = "-пусто-"


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "recipe")
    search_fields = ("pk",)
    empty_value_display = "-пусто-"


class BasketAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "recipe")
    search_fields = ("pk",)
    empty_value_display = "-пусто-"

class UserAdmin(admin.ModelAdmin):
    list_display = ("pk", "first_name", "last_name", "email", "username")
    search_fields = ("first_name",)
    empty_value_display = "-пусто-"


admin.site.register(Tag, TagAdmin)
# admin.site.register(TagRecipe, TagRecipeAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientRecipe, IngredientRecipeAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Basket, BasketAdmin)
admin.site.register(User, UserAdmin)