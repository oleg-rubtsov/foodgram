from django.core.checks import messages
from django.core.exceptions import ValidationError
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.contrib.auth import get_user_model
from recipes.models import Tag, Recipe, Ingredient, CHOICES, IngredientRecipe
from users.serializers import UsersSerializer
from base64 import b64decode
from django.core.files.base import ContentFile
import base64, uuid, six, imghdr


User = get_user_model()


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):

        if isinstance(data, six.string_types):
            if 'data:' in data and ';base64,' in data:
                header, data = data.split(';base64,')

            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            file_name = str(uuid.uuid4())[:12]
            file_extension = self.get_file_extension(file_name, decoded_file)
            complete_file_name = "%s.%s" % (file_name, file_extension, )
            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension




class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    # ingredient_name = serializers.CharField(source='name')

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit') 


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.FloatField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount') #ingredient_


class IngredientRecipeReturnSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    # amount = serializers.FloatField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount') #ingredient_


class IngredientRecipeListSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')
    
    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReturnSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField('get_ingredients')
    # ingredients = IngredientRecipeListSerializer(many=True, required=True)
    # images = Base64Conventor
    # tag = serializers.SlugRelatedField(
    #     queryset=Tag.objects.all(),
    #     slug_field='slug',
    #     many=True
    # )
    #tags = serializers.SerializerMethodField('get_tags')
    author = UsersSerializer(read_only=True)
    image = Base64ImageField()

    def get_ingredients(self, obj):
        queryset = IngredientRecipe.objects.filter(recipe=obj)
        return  IngredientRecipeReturnSerializer(queryset, many=True).data

    # def get_tags(self, obj):
    #     queryset = obj.tags
    #     #return TagSerializer(queryset, many=True).data
    #     return queryset


    class Meta:     
        model = Recipe
        fields = ('ingredients', 'tags', 'name', 'text',
                  'author', 'cooking_time', 'image')



class RecipeListSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField('get_ingredients')
    # ingredients = IngredientRecipeListSerializer(many=True, required=True)
    # images = Base64Conventor
    # tags = serializers.SerializerMethodField('get_tags')
    tags = TagSerializer(many=True, read_only=True)
    author = UsersSerializer(read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)

    def get_ingredients(self, obj):
        queryset = IngredientRecipe.objects.filter(recipe=obj)
        return IngredientRecipeListSerializer(queryset, many=True).data
    
    # def get_tags(self, obj):
    #     queryset = obj.tags
    #     return TagSerializer(queryset, many=True).data

    class Meta:     
        model = Recipe
        fields = ('id', 'ingredients', 'tags', 'name', 'text',
                  'cooking_time', 'author', 'image', 'is_favorited', 'is_in_shopping_cart')





class RecipeSerializer(serializers.ModelSerializer):
    # ingredients = IngredientSerializer(many=True, required=False)
    # tag = serializers.SlugRelatedField(
    #     queryset=Tag.objects.all(),
    #     slug_field='slug',
    #     many=True
    # )
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    ingredients = IngredientRecipeSerializer(many=True)
    image = Base64ImageField()
    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'text', 'ingredients', 'author',
                  'cooking_time', 'tags', 'image', 'is_favorited', 'is_in_shopping_cart')
        read_only_fields = ('author',)

    def create_tags(self, tags, recipe):
        for tag in tags:
            recipe.tags.add(tag)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            # current_ingredient, status = Ingredient.objects.get(
            #     pk=ingredient['ingredient']) # ingredient_
            IngredientRecipe.objects.create(
                ingredient=ingredient['id'], recipe=recipe, amount=ingredient['amount'])
        self.create_tags(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        IngredientRecipe.objects.filter(recipe=instance).all().delete()
        instance.tags.clear()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        #recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            # current_ingredient, status = Ingredient.objects.get(
            #     pk=ingredient['ingredient']) # ingredient_
            IngredientRecipe.objects.create(
                ingredient=ingredient['id'], recipe=instance, amount=ingredient['amount'])
        self.create_tags(tags, instance)
        instance.image = validated_data.get("image", instance.image)
        instance.name = validated_data.get("name", instance.name)
        instance.text = validated_data.get("text", instance.text)
        instance.cooking_time = validated_data.get("cooking_time", instance.cooking_time)
        instance.save()

        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReturnSerializer(instance, context=context).data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


