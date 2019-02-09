from rest_framework import serializers
from rest_auth.registration.serializers import RegisterSerializer

from games import models


class CustomRegisterSerializer(RegisterSerializer):

    name = serializers.CharField(required=True)
    surname = serializers.CharField(required=True)

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
        d['name'] = self.validated_data.get('name', 'Имя')
        d['surname'] = self.validated_data.get('surname', 'Фамилия')
        return d


class CustomUserDetailsSerializer(serializers.ModelSerializer):

    name = serializers.CharField(required=True, max_length=100)
    surname = serializers.CharField(required=True, max_length=100)

    class Meta:
        model = models.User
        fields = ('username', 'email', 'phone', 'name', 'surname')
        read_only_fields = ('username',)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = '__all__'


class ChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Child
        fields = '__all__'

    parent = UserSerializer(read_only=True)


class CommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Comments
        fields = '__all__'

    # child = ChildSerializer()


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Material
        fields = '__all__'


class FormSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Form
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = '__all__'


class QuantitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Quantity
        fields = '__all__'


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SubCategory
        fields = '__all__'


class FuncQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FunctionalQuestion
        fields = '__all__'


class CompQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CompoundQuestion
        fields = '__all__'


class DefQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DefinitionQuestion
        fields = '__all__'


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Color
        fields = '__all__'


class Game_1_Obj_Serializer(serializers.ModelSerializer):
    material = MaterialSerializer()
    form = FormSerializer()
    category = CategorySerializer()
    quantity = QuantitySerializer()
    sub_category = SubCategorySerializer()
    functional_question = FuncQuestionSerializer()
    compound_question = CompQuestionSerializer()
    definition_question = DefQuestionSerializer()
    color = ColorSerializer()

    class Meta:
        model = models.Game_1_obj
        exclude = ()


class StatisticSerizlier(serializers.ModelSerializer):
    class Meta:
        model = models.Statistic
        exclude = ()


class Game_2_Level_1_Obj_Serializer(serializers.ModelSerializer):
    class Meta:
        model = models.Game_2_Obj_Level_1
        exclude = ('last_changed',)


class Game_2_Level_2_Obj_Serializer(serializers.ModelSerializer):
    class Meta:
        model = models.Game_2_Obj_Level_2
        exclude = ('last_changed',)


class Game_2_Level_3_Obj_Serializer(serializers.ModelSerializer):
    class Meta:
        model = models.Game_2_Obj_Level_3
        exclude = ('last_changed',)


class Game_3_Obj_Serializer(serializers.ModelSerializer):
    class Meta:
        model = models.Game_3_Obj
        exclude = ('last_changed',)


class ImageUploadSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ImageUpload
        fields = '__all__'
