import logging

from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from games import models
from . import serializers

logger = logging.getLogger(__name__)


@csrf_exempt
@api_view(['GET'])
@permission_classes((AllowAny,))
def get_user(request, **kwargs):
    key = kwargs.get('key')
    token_obj = Token.objects.filter(key=key)
    if token_obj.exists():
        return Response(serializers.UserSerializer(token_obj.user).data)
    raise Http404


@csrf_exempt
@api_view(['GET'])
@permission_classes((AllowAny,))
def get_childs(request, **kwargs):
    key = kwargs.get('key')
    user = Token.objects.get(key=key).user
    childs = models.Child.objects.filter(parent=user)
    if childs.exist():
        data = [serializers.ChildSerializer(child).data for child in childs]
        return Response(data)
    else:
        raise Http404


@csrf_exempt
@api_view(['POST'])
@permission_classes((AllowAny,))
def append_child(request, **kwargs):
    key = kwargs.get('key')
    # user = Token.objects.get(key=key).user
    serialized_child = serializers.ChildSerializer(request.data)
    if serialized_child.is_valid():
        serialized_child.save()
        return Response(serialized_child.data, status=status.HTTP_201_CREATED)
    return Response(serialized_child.errors, status=status.HTTP_400_BAD_REQUEST)


class ChildViewSet(viewsets.ModelViewSet):
    queryset = serializers.Child.objects.all()
    serializer_class = serializers.ChildSerializer
    permission_classes = (permissions.AllowAny,)


class UserViewSet(viewsets.ModelViewSet):
    queryset = serializers.User.objects.all()
    serializer_class = serializers.UserSerializer
    lookup_field = 'username'
    permission_classes = (permissions.AllowAny,)


class CommentsViewSet(viewsets.ModelViewSet):
    queryset = serializers.Comments.objects.all()
    serializer_class = serializers.CommentsSerializer
    permission_classes = (permissions.AllowAny,)


class UserList(APIView):
    def get(self, request, format=None):
        users = serializers.User.objects.all()
        serializer = serializers.UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = serializers.UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetails(APIView):
    def get_object(self, username):
        try:
            return serializers.User.objects.get(username=username)
        except serializers.User.DoesNotExist:
            raise Http404

    def get(self, request, username, format=None):
        user = self.get_object(username)
        serializer = serializers.UserSerializer(user)
        return Response(serializer.data)

    def put(self, request, username, format=None):
        user = self.get_object(username)
        serializer = serializers.UserSerializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, username, format=None):
        upload = self.get_object(username)
        upload.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
