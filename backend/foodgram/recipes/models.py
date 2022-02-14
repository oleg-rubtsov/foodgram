from django.contrib.auth.models import AbstractUser
from django.db import models
from .validators import validate_even
from autoslug import AutoSlugField
from django.utils.text import slugify


class User(AbstractUser):
    username = models.CharField(
        max_length=200, verbose_name='Логин', unique=True, blank=True
    )
    email = models.EmailField(
        blank=False, unique=True, verbose_name='Email'
    )
    first_name = models.CharField(
        max_length=200, verbose_name='Имя'
    )
    last_name = models.CharField(max_length=200, verbose_name='Фамилия')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def get_favorite_count(self):
        return Favorite.objects.filter(user=self).count()
    get_favorite_count.short_description = 'Количество рецептов в избранном'

    def get_follow_count(self):
        return Follow.objects.filter(user=self).count()
    get_follow_count.short_description = 'Количество подписок'

    def get_basket_count(self):
        return Basket.objects.filter(user=self).count()
    get_basket_count.short_description = 'Количество рецептов в корзине'

    def __str__(self):
        return self.username


class Ingredient(models.Model):
    name = models.CharField(
        max_length=100, verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=50, verbose_name='Единицы измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        related_name='ingredients_ir',
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        "Recipe", on_delete=models.CASCADE,
        related_name='ingredient_recipe',
        verbose_name='Рецепт'
    )
    amount = models.IntegerField(
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Ингредиент-рецепт'
        verbose_name_plural = 'Ингредиент-рецепт'

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'


class Recipe(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    image = models.ImageField(
        upload_to='recipes/images/', blank=True,
        null=True, verbose_name='Картинка'
    )
    text = models.CharField(
        max_length=2000, verbose_name='Текстовое описание'
    )
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор публикации'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    cooking_time = models.IntegerField(
        validators=[validate_even],
        verbose_name='Время приготовления в минутах'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    tags = models.ManyToManyField(
        'Tag',
        related_name="recipe",
        related_query_name="recipes",
        verbose_name='Теги'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def get_ingredients(self):
        tmp = IngredientRecipe.objects.filter(recipe=self)
        return "\n".join([f'{p.ingredient.name} - {p.amount} '
                          f'{p.ingredient.measurement_unit}' for p in tmp])
    get_ingredients.short_description = 'Ингредиенты'

    def get_tags(self):
        return "\n".join([p.name for p in self.tags.all()])
    get_tags.short_description = 'Теги'

    def get_favorite_count(self):
        return Favorite.objects.filter(recipe=self).count()
    get_favorite_count.short_description = 'Количество добавлений в избранное'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    color = models.CharField(max_length=16, verbose_name='Цветовой HEX-код')
    slug = models.SlugField(unique=True, verbose_name='Slug')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['-name']

    def __str__(self):
        return self.name


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Пользователь'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'
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
        related_name='user_fav',
        verbose_name='Пользователь'        
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
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
        related_name='user_basket',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='in_basket',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_object_basket'
            ),
        ]

    def __str__(self):
        return self.recipe.name
