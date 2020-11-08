# from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.decorators import action
from .serializers import *
from .models import *

class LoginViewSet(viewsets.ViewSet):
    serializer_class = AuthTokenSerializer

    def create(self, request):
        user = UserAccount.objects.filter(email = request.data.get('username')).first()
        if user is None:
            return Response({'message': 'No user found', 'status': False, 'data': {}})

        serializer = self.serializer_class(data = request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user = user)
            return Response({'message': 'Success', 'status': True, 'data':{
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'token': token.key
            }})
        return Response({'message': 'Login failed', 'status': False, 'data': {}})

class RegisterViewSet(viewsets.ViewSet):
    serializer_class = UserAccountSerializer

    def create(self, request):
        serializer = UserAccountSerializer(data = request.data)
        if serializer.is_valid(raise_exception=True):
            user = UserAccount(email=serializer.data.get('email'),
                               name=serializer.data.get('name'))
            user.set_password(request.data.get('password'))
            user.save()
            return Response({'message': 'Success','statu':True, 'data': serializer.data})

class CategoryViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    serializer_class = CategoryPlainSerializer

    def create(self, request):
        serializer = CategoryPlainSerializer(data= request.data)
        if serializer.is_valid(raise_exception=True):
            category = Category(name= serializer.data.get('name'),
                                user=request.user)
            category.save()
            return Response({'message': 'Success', 'status': True, 'data': serializer.data})

    def list(self, request):
        categories = Category.objects.filter(user = request.user)
        serializer = CategoryPlainSerializer(categories, many=True)
        return Response({'message': 'Success', 'status': True, 'data': serializer.data})

    def retrieve(self, request, pk = None):
        category = Category.objects.filter(id = pk).first()
        if category is None:
            return Response({'message': 'Data not found', 'status': False, 'data': {}})
        else:
            serializer = CategoryPlainSerializer(category,many=False)
            return Response({'message': 'Success', 'status': True, 'data': serializer.data})

    def partial_update(self, request, pk = None):
        category = Category.objects.filter(id = pk).first()
        if category is None:
            return Response({'message': 'Data not found', 'status': False, 'data': {}})
        else:
            serializer = CategoryPlainSerializer(category, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response({'message': 'Success', 'status': True, 'data': serializer.data})

    def destroy(self, request, pk = None):
        category = Category.objects.filter(id = pk).first()
        if category is None:
            return Response({'message': 'Data not found', 'status': False, 'data': {}})
        else:
            category.delete()
            return Response({'message': 'Success delete', 'status': True, 'data': {}})