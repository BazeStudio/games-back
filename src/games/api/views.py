import logging
from datetime import datetime, timedelta
from django.core.mail import send_mail, EmailMessage
import csv
from io import StringIO
import hashlib, uuid

import requests
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import Http404
from django.urls.exceptions import NoReverseMatch
from django.views.decorators.csrf import csrf_exempt
from rest_auth.registration.views import RegisterView
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.parsers import FormParser, MultiPartParser

from rest_framework.response import Response, SimpleTemplateResponse
from rest_framework.views import APIView
from random import randint
from django.db.models import Q
import vk

from games import models
from . import serializers

logger = logging.getLogger(__name__)


class FileUploadViewSet(viewsets.ModelViewSet):
    queryset = models.ImageUpload.objects.all()
    serializer_class = serializers.ImageUploadSerializer
    parser_classes = (MultiPartParser, FormParser,)
    permission_classes = (permissions.AllowAny,)

    def perform_create(self, serializer):
        serializer.save(datafile=self.request.data.get('datafile'))


def send_sms(phone, subject, api_id='5C88E140-FB99-A47D-C5D3-81D3473364AE'):
    logger.info('Send sms to %s' % phone)

    if type(subject) == str:
        subject = subject.replace(" ", "+")

    url = "https://sms.ru/sms/send?api_id=%s&to=%s&msg=%s&json=1" % (api_id, phone, subject)
    return requests.get(url)


@csrf_exempt
@api_view(['GET', 'PUT'])
@permission_classes((AllowAny,))
def get_user(request, **kwargs):
    key = kwargs.get('key')
    token_obj = Token.objects.filter(key=key)
    if token_obj.exists():
        user = token_obj.get().user
    else:
        raise Http404

    if request.method == 'GET':
        return Response(serializers.UserSerializer(user).data)

    if request.method == 'PUT':

        try:
            fields = [f.name for f in models.User._meta.get_fields(include_parents=False)]
            non_changeable = [
                'date_joined', 'groups', 'id', 'is_active', 'is_staff','is_superuser', 'last_login',
                'password', 'user_permissions'
            ]
            for key, value in request.data.items():
                if key in fields and not key in non_changeable:
                    setattr(user, key, value)
            user.save()
            return Response(serializers.UserSerializer(user).data, status=status.HTTP_201_CREATED)

        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    raise Http404


@csrf_exempt
@api_view(['POST'])
@permission_classes((AllowAny,))
def user_approve(request, **kwargs):
    key = kwargs.get('key')

    token_obj = Token.objects.filter(key=key)
    if token_obj.exists():
        user = token_obj.get().user
    else:
        raise Http404

    if request.method == 'POST':
        code = request.data.get('code', None)

        if code:
            if user.random_number == int(code):
                user.is_active = True
                user.save()
                return Response(status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Missing code'}, status=status.HTTP_400_BAD_REQUEST)

    raise Http404


@csrf_exempt
@api_view(['GET'])
@permission_classes((AllowAny,))
def email_confirmation(request, **kwargs):
    key = kwargs.get('key')

    token_obj = Token.objects.filter(key=key)
    if token_obj.exists():
        user = token_obj.get().user
    else:
        return SimpleTemplateResponse('entities/not_confirm.html')

    if request.method == 'GET':
        user.is_active = True
        user.save()
        return SimpleTemplateResponse('entities/confirm.html')

    raise Http404


@csrf_exempt
@api_view(['GET'])
@permission_classes((AllowAny,))
def send_sms_to_user(request, **kwargs):
    key = kwargs.get('key')
    token_obj = Token.objects.filter(key=key)
    if token_obj.exists():
        user = token_obj.get().user
    else:
        raise Http404

    if request.method == 'GET':

        random_value = randint(1000, 9999)
        user.random_number = random_value
        user.save()
        if user.phone:
            send_sms(user.phone[1:], 'Kit4Kid code: %s' % random_value)
        else:
            return Response({"detail": "User doesn't have phone number"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'code': random_value}, status=status.HTTP_200_OK)

    raise Http404


@csrf_exempt
@api_view(['POST'])
@permission_classes((AllowAny,))
def reset_password(request, **kwargs):

    if request.method == 'POST':
        username = request.data.get('username', None)
        send_type = request.data.get('type', None)
        if not username:
            return Response({"detail": "Missing username"}, status=status.HTTP_400_BAD_REQUEST)

        if not send_type:
            return Response({"detail": "Missing type"}, status=status.HTTP_400_BAD_REQUEST)

        if send_type not in ['phone', 'email']:
            return Response({"detail": "Invalid type {}".format(send_type)}, status=status.HTTP_400_BAD_REQUEST)

        user = models.User.objects.filter(username=username)
        if not user.exists():
            raise Http404
        else:
            user = user.get()

        new_password = models.User.objects.make_random_password(length=2)
        new_password += 'A' + str(randint(0, 9))

        try:
            validate_password(new_password)
        except ValidationError as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        if user.phone and send_type == 'phone':
            send_sms(user.phone[1:], 'Kit4Kid new password: %s' % new_password)
        elif user.email and send_type == 'email':
            send_mail('Смена пароля Kit-4-Kid', 'Kit4Kid new password: %s' % new_password,
                      'info@kit-4-kid', (user.email,), fail_silently=False)
        else:
            return Response({"detail": "User doesn't have phone number"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializers.UserSerializer(user).data)


@csrf_exempt
@api_view(['POST'])
@permission_classes((AllowAny,))
def change_password(request, **kwargs):
    key = kwargs.get('key')
    token_obj = Token.objects.filter(key=key)
    if token_obj.exists():
        user = token_obj.get().user
    else:
        raise Http404

    if request.method == "POST":
        current_password = request.data.get('current_password', None)
        new_password = request.data.get('new_password', None)

        if not current_password:
            return Response({"detail": "Missing current_password"}, status=status.HTTP_400_BAD_REQUEST)

        if not new_password:
            return Response({"detail": "Missing new_password"}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(current_password):
            return Response({"detail": "Incorrect current password"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(new_password)
        except ValidationError as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response(status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST', 'GET', 'DELETE', 'PUT'])
@permission_classes((AllowAny,))
def child(request, **kwargs):
    """
    :param request data:
    {
        "name": "Олег",
        "birthday": "2006-10-25"
        "gender": "Мужсёкой", ("Женский")
        "photo": "/url/to/img"
    }
    """
    key = kwargs.get('key')
    token_obj = Token.objects.filter(key=key)

    if token_obj.exists():
        user = token_obj.get().user
    else:
        raise Http404

    if request.method == "POST":

        serialized_child = serializers.ChildSerializer(data=request.data)
        if serialized_child.is_valid():
            serialized_child.validated_data['parent'] = user
            serialized_child.save()
            return Response(serialized_child.data, status=status.HTTP_201_CREATED)
        return Response(serialized_child.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "GET":

        childs = models.Child.objects.filter(parent=user)
        if childs.exists():
            data = serializers.ChildSerializer(childs, many=True).data
            return Response(data)
        else:
            return Response([], status=status.HTTP_200_OK)

    if request.method == 'DELETE':

        if request.data['id']:
            ch = models.Child.objects.filter(id=request.data['id'], parent__id=user.id)
            if ch.exists():
                ch.delete()
                return Response(status=status.HTTP_200_OK)
            else:
                raise Http404
        else:
            return Response({"detail": "Missing ID of child"}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'PUT':
        if request.data.get('id', None):

            try:
                ch = models.Child.objects.filter(id=request.data['id'], parent__id=user.id)
                if ch.exists():
                    ch = ch.get()
                    fields = [f.name for f in models.Child._meta.get_fields(include_parents=False)]
                    non_changeable = ['id']
                    for key, value in request.data.items():
                        if key in fields and key not in non_changeable:
                            setattr(ch, key, value)
                    ch.save()
                    return Response(serializers.ChildSerializer(ch).data, status=status.HTTP_201_CREATED)
                else:
                    raise Http404
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({"detail": "Missing ID of child"}, status=status.HTTP_400_BAD_REQUEST)

    else:
        raise Http404


@csrf_exempt
@api_view(['GET'])
@permission_classes((AllowAny,))
def send_statistics(request, **kwargs):
    key = kwargs.get('key')
    token_obj = Token.objects.filter(key=key)

    if token_obj.exists():
        user = token_obj.get().user
    else:
        raise Http404

    if user.email:
        statistic = []

        for child in user.child_set.all():
            statistic += models.Statistic.objects.filter(child=child)

        attachment_csv_file = StringIO()
        statistic_fieldnames = [field.name for field in models.Statistic._meta.fields
                                if field.name not in ['id', 'mistakes_count']]
        writer = csv.DictWriter(attachment_csv_file, fieldnames=statistic_fieldnames)
        writer.writerow({
                'child': 'Имя',
                'game': 'Номер игры',
                'level': 'Уровень',
                'start_time': 'Время начала',
                'continuance': 'Продолжительность (в секундах)',
                'correct_percentage': 'Процент верно выполненных'
            })

        for s in statistic:
            row = {
                'child': s.child.name,
                'game': s.game,
                'level': s.level,
                'start_time': s.start_time,
                'continuance': s.continuance,
                'correct_percentage': s.correct_percentage
            }
            writer.writerow(row)

        mail = EmailMessage('Статистика Kit-4-Kid', 'Здравствуйте.\n\nСтатистика игр по Вашим детям:\nИгра 1 - сопоставления,\nИгра 2 - Различения,\nИгра 3 - Категории,\nИгра 4 - Последовательности,\nИгра 5 - Глаголы\n\n\nС уважением,\nадминистрация Kit-4-Kid', 'info@kit-4-kid', (user.email,))
        mail.attach('statistics.csv', attachment_csv_file.getvalue(), 'text/csv')
        mail.send(fail_silently=True)
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(data={'detail': 'Missing email'}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['GET'])
@permission_classes((AllowAny,))
def get_first_game_objects_for_update(request, **kwargs):
    dt = datetime.strptime(kwargs.get('date'), '%Y-%m-%d')
    objs = models.Game_1_obj.objects.filter(last_changed__gte=dt)
    return Response(serializers.Game_1_Obj_Serializer(objs, many=True).data)


@csrf_exempt
@api_view(['GET'])
@permission_classes((AllowAny,))
def get_second_array_first_level(request, **kwargs):
    dt = datetime.strptime(kwargs.get('date'), '%Y-%m-%d')
    objs = models.Game_2_Obj_Level_1.objects.filter(last_changed__gte=dt)
    return Response(serializers.Game_2_Level_1_Obj_Serializer(objs, many=True).data)


@csrf_exempt
@api_view(['GET'])
@permission_classes((AllowAny,))
def get_second_array_second_level(request, **kwargs):
    dt = datetime.strptime(kwargs.get('date'), '%Y-%m-%d')
    objs = models.Game_2_Obj_Level_2.objects.filter(last_changed__gte=dt)
    return Response(serializers.Game_2_Level_2_Obj_Serializer(objs, many=True).data)


@csrf_exempt
@api_view(['GET'])
@permission_classes((AllowAny,))
def get_second_array_third_level(request, **kwargs):
    dt = datetime.strptime(kwargs.get('date'), '%Y-%m-%d')
    objs = models.Game_2_Obj_Level_3.objects.filter(last_changed__gte=dt)
    return Response(serializers.Game_2_Level_3_Obj_Serializer(objs, many=True).data)


@csrf_exempt
@api_view(['GET'])
@permission_classes((AllowAny,))
def get_third_array(request, **kwargs):
    dt = datetime.strptime(kwargs.get('date'), '%Y-%m-%d')
    objs = models.Game_3_Obj.objects.filter(last_changed__gte=dt)
    return Response(serializers.Game_3_Obj_Serializer(objs, many=True).data)


@csrf_exempt
@api_view(['GET'])
@permission_classes((AllowAny,))
def check_update(request, **kwargs):
    dt = datetime.strptime(kwargs.get('date'), '%Y-%m-%dT%H:%M:%S') + timedelta(hours=3)
    objs_game_1 = models.Game_1_obj.objects.filter(last_changed__gte=dt).count()
    objs_game_2_level_1 = models.Game_2_Obj_Level_1.objects.filter(last_changed__gte=dt).count()
    objs_game_2_level_2 = models.Game_2_Obj_Level_2.objects.filter(last_changed__gte=dt).count()
    objs_game_2_level_3 = models.Game_2_Obj_Level_3.objects.filter(last_changed__gte=dt).count()
    objs_game_3 = models.Game_3_Obj.objects.filter(last_changed__gte=dt).count()
    return Response(
        {
            'Game_1': objs_game_1 > 0,
            'Game_2_level_1': objs_game_2_level_1 > 0,
            'Game_2_level_2': objs_game_2_level_2 > 0,
            'Game_2_level_3': objs_game_2_level_3 > 0,
            'Game_3': objs_game_3 > 0
        }
    )


@csrf_exempt
@api_view(['GET'])
@permission_classes((AllowAny,))
def get_child_comments(request, **kwargs):
    child_id = kwargs.get('child_id')
    qs = models.Comments.objects.filter(child__id=child_id)
    data = serializers.CommentsSerializer(qs, many=True).data
    return Response(data)


@csrf_exempt
@api_view(['GET'])
@permission_classes((AllowAny,))
def get_child_statistics(request, **kwargs):
    child_id = kwargs.get('child_id')
    qs = models.Statistic.objects.filter(child__id=child_id)
    data = serializers.StatisticSerizlier(qs, many=True).data
    return Response(data)


@csrf_exempt
@api_view(['POST'])
@permission_classes((AllowAny,))
def social_registration(request, **kwargs):
    token = request.data.get('token', None)
    social = request.data.get('social', None)
    user_id = request.data.get('user_id', None)

    if not token or not social:
        return Response({'detail': 'Missing token or social type'}, status=status.HTTP_400_BAD_REQUEST)

    if social == 'vk':
        kw = {'vk_token': token}
    elif social == 'facebook':
        kw = {'facebook_token': token}
    else:
        return Response({'detail': 'Incorrect social type (options: "vk", "facebook")'},
                        status=status.HTTP_400_BAD_REQUEST)

    if models.User.objects.filter(**kw).exists():
        return Response({'detail': 'User with access token %s already exist' % token},
                        status=status.HTTP_400_BAD_REQUEST)

    salt = uuid.uuid4().hex
    hashed_password = hashlib.sha512((token + salt).encode('utf-8')).hexdigest()
    data = {
        'username': token,
        'email': None,
        'phone': None,
        'is_active': True,
        'is_superuser': False,
        'is_staff': False,
    }
    if social == 'vk':
        session = vk.Session(access_token=token)
        vk_api = vk.API(session, v=3)
        if not user_id:
            return Response({'detail': 'Missing user_id'}, status=status.HTTP_400_BAD_REQUEST)
        response = vk_api.users.get(user_id=user_id)[0]
        data.update({
            'name': response['first_name'],
            'surname': response['last_name'],
            'vk_token': token,
        })
    elif social == 'facebook':
        data.update({
            'name': '',
            'surname': '',
            'facebook_token': token,
        })

    user = models.User.objects.create(**data)
    user.set_password(hashed_password)
    user.save()
    token_obj = Token.objects.create(user=user)
    return Response({'key': token_obj.key}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
@permission_classes((AllowAny,))
def social_login(request, **kwargs):
    token = request.data.get('token', None)
    social = request.data.get('social', None)
    if not token or not social:
        raise Http404

    if social not in ['vk', 'facebook']:
        return Response({'detail': 'Incorrect social type (options: "vk", "facebook")'},
                        status=status.HTTP_400_BAD_REQUEST)

    user = models.User.objects.filter(Q(vk_token=token) | Q(facebook_token=token))
    if user.exists():
        return Response({'key': Token.objects.get(user=user.get()).key}, status=status.HTTP_200_OK)
    else:
        raise Http404


class ChildViewSet(viewsets.ModelViewSet):
    queryset = models.Child.objects.all()
    serializer_class = serializers.ChildSerializer
    permission_classes = (permissions.AllowAny,)


class UserViewSet(viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    lookup_field = 'username'
    permission_classes = (permissions.AllowAny,)


class CommentsViewSet(viewsets.ModelViewSet):
    queryset = models.Comments.objects.all()
    serializer_class = serializers.CommentsSerializer
    permission_classes = (permissions.AllowAny,)

    def get_serializer(self, *args, **kwargs):
        """ if an array is passed, set serializer to many """
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)


class StatisticViewSet(viewsets.ModelViewSet):
    queryset = models.Statistic.objects.all()
    serializer_class = serializers.StatisticSerizlier
    permission_classes = (permissions.AllowAny,)

    def get_serializer(self, *args, **kwargs):
        """ if an array is passed, set serializer to many """
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)


class UserList(APIView):
    def get(self, request, format=None):
        users = models.User.objects.all()
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
            return models.User.objects.get(username=username)
        except models.User.DoesNotExist:
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


class CustomRegisterView(RegisterView):

    def get_response_data(self, user):
        d = super().get_response_data(user)
        d['code'] = user.random_number
        return d

    def perform_create(self, serializer):
        try:
            return super().perform_create(serializer)
        except NoReverseMatch:
            random_value = randint(1000, 9999)
            user = models.User.objects.get(username=self.request.data['username'])
            user.random_number = random_value
            user.save()
            if user.phone:
                send_sms(user.phone[1:], 'Kit4Kid code: %s' % random_value)
            if '@' in user.username:
                token_obj = Token.objects.get(user=user)
                url = 'http://142.93.100.226/api/v1/users/{key}/email_confirmation/'.format(key=token_obj.key)
                send_mail('Авторизация Kit-4-Kid',
                          'Для подтверждения регистрации в мобильном приложении Kit4Kid перейдите по ссылке: %s' % url,
                          'info@kit-4-kid.com', (user.email,), fail_silently=False)

            return user
