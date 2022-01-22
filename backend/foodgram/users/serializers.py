from django.core.exceptions import ValidationError
from django.db.models.fields import EmailField
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from recipes.models import Follow
from django.utils.translation import gettext as _
from django.contrib.auth import authenticate

User = get_user_model()


class UsersSerializer(serializers.ModelSerializer):
    # following = serializers.SerializerMethodField()
    # followers = serializers.SerializerMethodField()
    #is_subscribed = serializers.SerializerMethodField('get_serializer_context')
    is_subscribed = serializers.BooleanField(default=False)
    # def save(self):
    #     is_subscribed = self.validated_data['is_subscribed']
    #     # message = self.validated_data['message']
    #     # send_email(from=email, message=message) 

    # def get_serializer_context(self, obj):
    #     return False

    # def get_serializer_context(self, obj):
    #     followed = self.context.get("followed")
    #     if self.data in followed.user:
    #         return {'is_subscribed': True}
    #     else:
    #         return {'is_subscribed': False}

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name',
            'last_name', 'is_subscribed'
        )

    # def get_following(self, obj):
    #     return UserFollowingSerializer(obj.following.all(), many=True).data

    # def get_followers(self, obj):
    #     return UserFollowersSerializer(obj.followers.all(), many=True).data



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
    """
    Serializer for password change endpoint.
    """
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value


# class UserFollowingSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Follow
#         fields = ("id", "author")


# class UserFollowersSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Follow
#         fields = ("id", "user")

# class FollowSerializer(serializers.ModelSerializer):
#     user = serializers.SlugRelatedField(
#         queryset=User.objects.all(),
#         slug_field='username',
#         default=serializers.CurrentUserDefault()
#     )
#     following = SlugRelatedField(
#         slug_field='username',
#         queryset=User.objects.all()
#     )

#     class Meta:
#         fields = ['user', 'following']
#         model = Follow
#         validators = [
#             UniqueTogetherValidator(
#                 queryset=Follow.objects.all(),
#                 fields=['following', 'user']
#             )
#         ]

#     def validate_following(self, value):
#         if self.context['request'].user == value:
#             raise serializers.ValidationError('Вы уже подписаны!')
#         return value


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

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['email'] = email
        return attrs