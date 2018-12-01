from rest_framework import serializers
from rest_auth.registration.serializers import RegisterSerializer

from games.models import User, Comments, Child, Game_1_obj, Statistic


class CustomRegisterSerializer(RegisterSerializer):
    # phone = serializers.CharField(required=False, allow_blank=True)
    #
    # name = serializers.CharField(required=True)
    # surname = serializers.CharField(required=True)

    def validate_name(self, name):
        if not name:
            raise serializers.ValidationError('Не указано имя')
        return name

    def validate_surname(self, surname):
        if not surname:
            raise serializers.ValidationError('Не указана фамилия')
        return surname

    def get_cleaned_data(self):
        d = super(CustomRegisterSerializer, self).get_cleaned_data()
        d['phone'] = self.validated_data.get('phone', '')
        d['name'] = self.validated_data.get('name', 'Имя')
        d['surname'] = self.validated_data.get('surname', 'Фамилия')
        return d


class CustomUserDetailsSerializer(serializers.ModelSerializer):

    name = serializers.CharField(required=True, max_length=100)
    surname = serializers.CharField(required=True, max_length=100)

    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'name', 'surname')
        read_only_fields = ('username',)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class ChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Child
        fields = '__all__'

    parent = UserSerializer()


class CommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = '__all__'

    child = ChildSerializer()


class Game_1_Obj_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Game_1_obj
        exclude = ('id',)


class StatisticSerizlier(serializers.ModelSerializer):
    class Meta:
        model = Statistic
        exclude = ()
