from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        max_length=200, verbose_name='name of user', unique=True, blank=True
    )
    email = models.EmailField(
        blank=False, unique=True, verbose_name='email of user'
    )
    first_name = models.CharField(max_length=200, verbose_name='name')
    last_name = models.CharField(max_length=200, verbose_name='name2')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.username


class Ingredient(models.Model):
    name = models.CharField(
        max_length=50, verbose_name='ingredient name', unique=True
    )
    measurement_unit = models.CharField(
        max_length=50, verbose_name='measure name'
    )

    class Meta:
        verbose_name = 'ingredient'
        verbose_name_plural = 'ingredients'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey("Recipe", on_delete=models.CASCADE)
    amount = models.FloatField(max_length=10)

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'


class Recipe(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(
        upload_to='recipes/images/', blank=True, null=True
    )
    text = models.CharField(max_length=200)
    author = models.ForeignKey(
        User, related_name='recipes', on_delete=models.CASCADE)
    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientRecipe'
    )
    cooking_time = models.FloatField()
    pub_date = models.DateTimeField("date published", auto_now_add=True)


    class Meta:
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
    recipe_name = models.ManyToManyField(
        Recipe,
        related_name="tags",
        related_query_name="tag"
    )
    name = models.CharField(max_length=200, verbose_name='tag name')
    color = models.CharField(max_length=16)
    slug = models.SlugField(unique=True, verbose_name='tag_slug')

    class Meta:
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
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_object'
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
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_object'
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
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_object'
            ),
        ]

    def __str__(self):
        return self.recipe.name
