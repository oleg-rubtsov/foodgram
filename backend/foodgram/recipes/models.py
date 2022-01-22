from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


CHOICES = (
        ('#DC143C', 'Red'),
        ('#00FF7F', 'Green'),
        ('#EE82EE', 'Violet'),
    )



# class Tag(models.Model):
#     name = models.CharField(max_length=200, verbose_name='tag name')
#     color = models.CharField(max_length=16) # , choices=CHOICES
#     slug = models.SlugField(unique=True, verbose_name='tag slug')

#     class Meta:
#         ordering = ['-name']
#         verbose_name = 'tag'
#         verbose_name_plural = 'tags'

#     def __str__(self):
#         return self.name




class Ingredient(models.Model):
    name = models.CharField(max_length=50, verbose_name='ingredient name', unique=True)
    measurement_unit = models.CharField(max_length=50, verbose_name='measure name')

    class Meta:
        ordering = ['-name']
        verbose_name = 'ingredient'
        verbose_name_plural = 'ingredients'


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey("Recipe", on_delete=models.CASCADE)
    amount = models.FloatField(max_length=10)

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'



class Recipe(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='recipes/images/', blank=True, null=True)
    text = models.CharField(max_length=200)
    author = models.ForeignKey(
        User, related_name='recipes', on_delete=models.CASCADE)
    ingredients = models.ManyToManyField(Ingredient, through='IngredientRecipe')
    # tags = models.ManyToManyField(
    #     Tag,
    #     related_name='recipes',
    #     blank=True,
    #     verbose_name='tag'
    # )  # , through='TagRecipe'
    cooking_time = models.FloatField()

    def get_ingredients(self):
        tmp = IngredientRecipe.objects.filter(recipe=self)
        return "\n".join([p.ingredient.name for p in tmp])
    
    def get_tags(self):
        #tmp = Recipe.objects.filter(recipe=self
        return "\n".join([p.name for p in self.tags.all()])

    def __str__(self):
        return self.name





# class TagRecipe(models.Model):
#     tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
#     recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

#     def __str__(self):
#         return f'{self.tag} {self.recipe}'

class Tag(models.Model):
    recipe_name = models.ManyToManyField(
        Recipe,
        related_name="tags",
        related_query_name="tag"
    )
    name = models.CharField(max_length=200, verbose_name='tag name')
    color = models.CharField(max_length=16) # , choices=CHOICES
    slug = models.SlugField(unique=True, verbose_name='tag slug')

    class Meta:
        ordering = ['-name']
        # verbose_name = 'tag'
        # verbose_name_plural = 'tags'

    def __str__(self):
        return self.name


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="followers")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="following")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_object'),
        ]

    def __str__(self):
        return self.user.username


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="user_fav")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name="favorites")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_object'),
        ]

    def __str__(self):
        return self.recipe.name


class Basket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="user_basket")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name="in_basket")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_object'),
        ]

    def __str__(self):
        return self.recipe.name