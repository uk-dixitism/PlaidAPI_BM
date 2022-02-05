from urllib import response
from django.http import HttpResponse
from django.shortcuts import render,redirect
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from user import serializers
from .serializers import UserLogin, UserRegistration
from django.contrib import auth
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated, AllowAny
import plaid
from .keys import *


client = plaid.Client(client_id=PLAID_CLIENT_ID,public_key=PLAID_PUBLIC_KEY ,secret=PLAID_SECRET, environment=PLAID_ENV, api_version='2020-09-14')


class Registration(APIView):
    
    def post(self,request):
        serializer = UserRegistration(data = request.data)
        
        if(serializer.is_valid()):
            user = UserRegistration.CreateUser(self,serializer.data)
            user.save()
            #user = serializer.save()
            token = Token.objects.create(user=user)
            json = serializer.data
            json['token'] = token.key
            return Response(data={
					'user':user.username,
					'email':user.email,
					'message':"Account Created"
					},status = status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Login(APIView):

    #permission_class = [AllowAny]
    
    def post(self, request):
        serializer = UserLogin(data=request.data)
        
        if serializer.is_valid():
    
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = auth.authenticate( request, username=username, password=password)
            
            if user is None:
                print('Hi')
                return HttpResponse("User does not exist")
            else:
                auth.login(request,user)
                token,created = Token.objects.get_or_create(user = user)
                return Response({
    				'token':token.key,
    				'email':user.email
    				},status = status.HTTP_200_OK)
            
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class Logout(APIView):
    
    permission_classes = [IsAuthenticated]
	
    def get(self,request):
        try:
            request.user.auth_token.delete()
        except (ObjectDoesNotExist):
            return Response(serializers.errors, status = status.HTTP_400_BAD_REQUEST)
        
        auth.logout(request)
        
        return Response({
			'success':'Logged Out'
			}, status = status.HTTP_200_OK)