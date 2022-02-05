from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.validators import UniqueValidator
from rest_framework import serializers
from django.contrib import auth
from django.contrib.auth.hashers import make_password


class UserRegistration(serializers.Serializer):

    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    username = serializers.CharField(max_length=100 , validators=[UniqueValidator(queryset=User.objects.all())])
    #password = serializers.CharField(min_length=8)
    password = serializers.CharField(
        write_only=True,
        required=True,
        help_text='Leave empty if no change needed',
        style={'input_type': 'password', 'placeholder': 'Password'}
    )
    def CreateUser(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        user = User.objects.create(**validated_data)
        return user
    # def CreateUser(self, validated_data):
    #     validated_data['password'] = make_password(validated_data.get('password'))
    #     return super(UserRegistration, self).create(validated_data)
    # class Meta:
    #     model = User
    #     fields = ['id', 'email', 'username', 'password']


class UserLogin(serializers.Serializer):
    
    username = serializers.CharField(max_length = 100, required = True)
    password = serializers.CharField(required = True, write_only = True)
	
    # class Meta:
    #     model = User
    #     fields = ['username', 'email', 'password']
