from django.core.exceptions import ValidationError
from django.db.models.fields import EmailField
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from recipes.models import Follow, User, Recipe
from django.utils.translation import gettext as _
from django.contrib.auth import authenticate



class RecipeSubscriptionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time'
        )



class UsersSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField('get_serializer_context')


    def get_serializer_context(self, obj):
        request = self.context.get('request')
        try:
            get_object_or_404(Follow, author=obj, user=request.user)
            return True
        except:
            return False

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name',
            'last_name', 'is_subscribed'
        )


class SubscriptionsSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField('get_serializer_context')
    recipes = serializers.SerializerMethodField('get_recipes')
    recipes_count = serializers.SerializerMethodField('get_recipes_count')

    def get_serializer_context(self, obj):
        request = self.context.get('request')

        # print(request.query_params)
        try:
            get_object_or_404(Follow, author=obj, user=request.user)
            return True
        except:
            return False
    
    def get_recipes_count(self, obj):
        recipes_count = Recipe.objects.filter(author=obj).count()
        return recipes_count
        
    def get_recipes(self, obj):
        try:
            request = self.context.get('request')
            query_params = request.query_params
            recipes_limit = int(query_params['recipes_limit'][0])
            queryset = Recipe.objects.filter(author=obj)[:recipes_limit]
            return RecipeSubscriptionsSerializer(queryset, many=True).data
        except:
            queryset = Recipe.objects.filter(author=obj)
            return RecipeSubscriptionsSerializer(queryset, many=True).data


    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name',
            'last_name', 'is_subscribed', 'recipes_count',
            'recipes'
        )







class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

        fields = ['email', 'username', 'first_name', 'last_name', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
        }


    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value


class CustomAuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField(label=_("email"))

    def __init__(self, *args, **kwargs):
        super(CustomAuthTokenSerializer, self).__init__(*args, **kwargs)
        self.fields['pass'] = serializers.CharField(
            label=_("Pass"),
            style={'input_type': 'password'},
            trim_whitespace=False
        )
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('pass')

        if email and password:

            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)

            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['email'] = email
        return attrs