from django.contrib.auth.models import AbstractUser
from django.db import models
from .validators import validate_even
from autoslug import AutoSlugField
from django.utils.text import slugify


class User(AbstractUser):
    username = models.CharField(
        max_length=200, verbose_name='user_username', unique=True, blank=True
    )
    email = models.EmailField(
        blank=False, unique=True, verbose_name='user_email'
    )
    first_name = models.CharField(
        max_length=200, verbose_name='user_first_name'
    )
    last_name = models.CharField(max_length=200, verbose_name='user_last_name')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return self.username


class Ingredient(models.Model):
    name = models.CharField(
        max_length=100, verbose_name='ingredient_name'
    )
    measurement_unit = models.CharField(
        max_length=50, verbose_name='ingredient_measure'
    )

    class Meta:
        verbose_name = 'ingredient'
        verbose_name_plural = 'ingredients'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        related_name='ingredients_ir'
    )
    recipe = models.ForeignKey(
        "Recipe", on_delete=models.CASCADE,
        related_name='ingredient_recipe'
    )
    amount = models.FloatField(
        max_length=10,
        verbose_name='IngredientRecipe_amount'
    )

    class Meta:
        verbose_name = 'IngredientRecipe'
        verbose_name_plural = 'IngredientRecipes'

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'


class Recipe(models.Model):
    name = models.CharField(max_length=50, verbose_name='Recipe_name')
    image = models.ImageField(
        upload_to='recipes/images/', blank=True,
        null=True, verbose_name='Recipe_image'
    )
    text = models.CharField(max_length=200, verbose_name='Recipe_text')
    author = models.ForeignKey(
        User, related_name='recipes', on_delete=models.CASCADE)
    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientRecipe', related_name='recipes'
    )
    cooking_time = models.IntegerField(
        validators=[validate_even], verbose_name='Recipe_cooking_time'
    )
    pub_date = models.DateTimeField(
        "date published", auto_now_add=True
    )
    tags = models.ManyToManyField(
        'Tag',
        related_name="recipe",
        related_query_name="recipes"
    )

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'
        ordering = ['-pub_date']

    def get_ingredients(self):
        tmp = IngredientRecipe.objects.filter(recipe=self)
        return "\n".join([p.ingredient.name for p in tmp])

    def get_tags(self):
        return "\n".join([p.name for p in self.tags.all()])

    def get_favorite_count(self):
        return Favorite.objects.filter(recipe=self).count()

    def __str__(self):
        return self.name


class Tag(models.Model):
    # recipe_name = models.ManyToManyField(
    #     Recipe,
    #     related_name="tags",
    #     related_query_name="tag"
    # )
    name = models.CharField(max_length=200, verbose_name='tag_name')
    color = models.CharField(max_length=16, verbose_name='tag_color')
    slug = models.SlugField(unique=True, verbose_name='tag_slug')

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['-name']

    def __str__(self):
        return self.name


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="followers"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="following"
    )

    class Meta:
        verbose_name = 'Follow'
        verbose_name_plural = 'Follows'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_object_follow'
            ),
        ]

    def __str__(self):
        return self.user.username


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="user_fav"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name="favorites"
    )

    class Meta:
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_object_favorite'
            ),
        ]

    def __str__(self):
        return self.recipe.name


class Basket(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="user_basket"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name="in_basket"
    )

    class Meta:
        verbose_name = 'Basket'
        verbose_name_plural = 'Baskets'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_object_basket'
            ),
        ]

    def __str__(self):
        return self.recipe.name
