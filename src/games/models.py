from random import randint

from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core import validators
from django.core.mail import send_mail
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.aggregates import Count
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .validators import validate_file_extension, validate_file_size


class MyUserManager(BaseUserManager):
    """
    A custom user manager to deal with emails as unique identifiers for auth
    instead of usernames. The default that's used is "UserManager"
    """

    def normalize_phone(self, phone, country_code=None):
        phone = phone.strip().lower()
        try:
            import phonenumbers
            phone_number = phonenumbers.parse(phone, country_code)
            phone = phonenumbers.format_number(
                phone_number, phonenumbers.PhoneNumberFormat.E164)
        except ImportError:
            pass

        return phone

    def _create_user(self, username, password,
                     is_staff, is_superuser, **extra_fields):
        """ Create EmailPhoneUser with the given email or phone and password.
        :param str username: user email or phone
        :param str password: user password
        :param bool is_staff: whether user staff or not
        :param bool is_superuser: whether user admin or not
        :return settings.AUTH_USER_MODEL user: user
        :raise ValueError: email or phone is not set
        :raise NumberParseException: phone does not have correct format
        """
        if not username:
            raise ValueError('The given email_or_phone must be set')

        if "@" in username:
            # email_or_phone = self.normalize_email(email_or_phone)
            username, email, phone = (username, username, "")
        else:
            username, email, phone = (username, "", username)

        now = timezone.now()
        is_active = extra_fields.pop("is_active", False)
        user = self.model(
            username=username,
            email=email,
            phone=phone,
            is_staff=is_staff,
            is_active=is_active,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password, **extra_fields):
        return self._create_user(username, password, False, False,
                                 **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        return self._create_user(username, password, True, True,
                                 **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """ Abstract User with the same behaviour as Django's default User."""

    username = models.CharField(
        _('email or phone'), max_length=255, unique=True, db_index=True,
        help_text=_('Required. 255 characters or fewer. Letters, digits and '
                    '@/./+/-/_ only.'),
        validators=[validators.RegexValidator(
            r'^[\w.@+-]+$', _(
                'Enter a valid username. '
                'This value may contain only letters, numbers '
                'and @/./+/-/_ characters.'
            ), 'invalid'),
        ],
        error_messages={
            'unique': _("A user with that username already exists."),
        })
    email = models.EmailField(_('email'), max_length=254, blank=True, null=True)
    phone = models.CharField(_('phone'), max_length=255, blank=True, null=True)

    is_staff = models.BooleanField(
        _('staff status'), default=False, help_text=_(
            'Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(
        _('active'), default=False, help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    name = models.CharField(verbose_name='Имя', max_length=100, null=True, blank=True)
    surname = models.CharField(verbose_name='Фамилия', max_length=100, null=True, blank=True)
    random_number = models.IntegerField(verbose_name='Код из смс', null=True, blank=True)

    photo = models.CharField(null=True, blank=True, max_length=100, verbose_name='Фото')

    objects = MyUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name', 'surname']

    vk_token = models.CharField(max_length=100, null=True, blank=True)
    facebook_token = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return '{} {}'.format(self.name, self.surname)

    class Meta:
        verbose_name = 'Пользователя (родителя)'
        verbose_name_plural = 'Пользователи (родители)'

    def get_full_name(self):
        """ Return the full name for the user."""
        return self.username

    def get_short_name(self):
        """ Return the short name for the user."""
        return self.username

    def email_user(self, subject, message, from_email=None, **kwargs):
        """ Send an email to this User."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class Child(models.Model):
    MAN = "Мужской"
    WOMAN = "Женский"

    GENDER = (
        (MAN, 'Мужской'),
        (WOMAN, 'Женский')
    )

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, null=False, verbose_name='Имя')
    birthday = models.DateField(null=False, verbose_name='Дата рождения')
    gender = models.CharField(max_length=7, choices=GENDER, null=False, verbose_name='Пол')
    photo = models.CharField(null=True, blank=True, max_length=100, verbose_name='Фото')

    parent = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name='Родитель')

    statistic_last_updated = models.DateTimeField(auto_now_add=True, editable=True, null=True,
                                                  verbose_name='Дата последнего обновления')

    def __str__(self):
        return self.name

    def set_statistic(self, json_obj):
        self.statistic_last_updated = timezone.now()
        self.status = json_obj
        self.save()

    class Meta:
        verbose_name = "Дети"
        verbose_name_plural = "Дети"


class Statistic(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, verbose_name='Ребенок')

    game = models.IntegerField(
        "Номер игры",
        null=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
        help_text='Целочисленное значение от 1 до 5'
    )

    level = models.IntegerField(
        "Уровень игры",
        null=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
        help_text='Целочисленное значение от 1 до 5'
    )

    start_time = models.DateTimeField(verbose_name='Время начала')
    continuance = models.IntegerField(verbose_name='Продолжительность', validators=[MinValueValidator(0)])

    mistakes_count = models.IntegerField(
        verbose_name='Количество ошибок',
        validators=[
            MinValueValidator(0),
        ],
    )

    correct_percentage = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
        null=False,
        verbose_name='Процент верно выполненных'
    )

    class Meta:
        verbose_name = "Статистика"
        verbose_name_plural = "Статистика"


class Comments(models.Model):
    text = models.CharField(max_length=1000)
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    last_changed = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def set_text(self, text):
        self.text = text
        self.last_changed = timezone.now()
        self.save()


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=30, null=False, verbose_name='Категория')

    category_eng = models.CharField(max_length=100, verbose_name='Категория на английском', null=False, blank=False,
                                       default='change me')

    audio = models.FileField(
        upload_to='audios/',
        validators=[
            validate_file_extension, validate_file_size
        ],
        null=True,
        blank=True,
        verbose_name='Аудио',
        help_text='до 5 мб',
    )

    audio_eng = models.FileField(
        upload_to='audios/',
        validators=[
            validate_file_extension, validate_file_size
        ],
        null=True,
        blank=True,
        verbose_name='Аудио на английском',
        help_text='до 5 мб',
    )

    @staticmethod
    def populate(values):
        Category.objects.bulk_create([Category(
            category=rus_val,
        ) for eng_val, rus_val in values.items()])

    def __str__(self):
        return self.category

    class Meta:
        verbose_name = u"Категория"
        verbose_name_plural = u"Категории"


class Color(models.Model):
    id = models.AutoField(primary_key=True)
    color = models.CharField(max_length=30, null=False, verbose_name='Цвет ID')
    description = models.CharField(max_length=100, null=False, blank=False, verbose_name='Название цвета',
                                   help_text='Впишите текст с нужным склонением выбранного цвета')

    color_eng = models.CharField(max_length=100, verbose_name='Цвет на английском',
                                 null=False, blank=False, default='change me')

    audio = models.FileField(
        upload_to='audios/',
        validators=[
            validate_file_extension, validate_file_size
        ],
        null=True,
        blank=True,
        verbose_name='Аудио',
        help_text='до 5 мб',
    )

    audio_eng = models.FileField(
        upload_to='audios/',
        validators=[
            validate_file_extension, validate_file_size
        ],
        null=True,
        blank=True,
        verbose_name='Аудио на английском',
        help_text='до 5 мб',
    )

    @staticmethod
    def populate(values):
        Color.objects.bulk_create([Color(
            color=rus_val,
        ) for eng_val, rus_val in values.items()])

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = u"Цвета"
        verbose_name_plural = u"Цвета"


class Material(models.Model):
    id = models.AutoField(primary_key=True)
    material = models.CharField(max_length=30, null=False, verbose_name='Материал')

    material_eng = models.CharField(max_length=100, verbose_name='Материал на английском', null=False, blank=False,
                                    default='change me')

    audio = models.FileField(
        upload_to='audios/',
        validators=[
            validate_file_extension, validate_file_size
        ],
        null=True,
        blank=True,
        verbose_name='Аудио',
        help_text='до 5 мб',
    )

    audio_eng = models.FileField(
        upload_to='audios/',
        validators=[
            validate_file_extension, validate_file_size
        ],
        null=True,
        blank=True,
        verbose_name='Аудио на английском',
        help_text='до 5 мб',
    )

    @staticmethod
    def populate(values):
        Material.objects.bulk_create([Material(
            material=rus_val,
        ) for eng_val, rus_val in values.items()])

    def __str__(self):
        return self.material

    class Meta:
        verbose_name = u"Материал"
        verbose_name_plural = u"Материал"


class Form(models.Model):
    id = models.AutoField(primary_key=True)
    form = models.CharField(max_length=30, null=False, verbose_name='Форма')
    form_eng = models.CharField(max_length=100, verbose_name='Форма на английском', null=False, blank=False,
                                       default='change me')

    audio = models.FileField(
        upload_to='audios/',
        validators=[
            validate_file_extension, validate_file_size
        ],
        null=True,
        blank=True,
        verbose_name='Аудио',
        help_text='до 5 мб',
    )

    audio_eng = models.FileField(
        upload_to='audios/',
        validators=[
            validate_file_extension, validate_file_size
        ],
        null=True,
        blank=True,
        verbose_name='Аудио на английском',
        help_text='до 5 мб',
    )

    @staticmethod
    def populate(values):
        Form.objects.bulk_create([Form(
            form=rus_val,
        ) for eng_val, rus_val in values.items()])

    def __str__(self):
        return self.form

    class Meta:
        verbose_name = u"Форма"
        verbose_name_plural = u"Форма"


class FunctionalQuestion(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.CharField(max_length=30, null=False, verbose_name='Функциональный вопрос')

    question_eng = models.CharField(max_length=100, verbose_name='Функциональный вопрос на английском',
                                               null=False, blank=False, default='change me')

    audio = models.FileField(
        upload_to='audios/',
        validators=[
            validate_file_extension, validate_file_size
        ],
        null=True,
        blank=True,
        verbose_name='Аудио',
        help_text='до 5 мб',
    )

    audio_eng = models.FileField(
        upload_to='audios/',
        validators=[
            validate_file_extension, validate_file_size
        ],
        null=True,
        blank=True,
        verbose_name='Аудио на английском',
        help_text='до 5 мб',
    )

    @staticmethod
    def populate(values):
        FunctionalQuestion.objects.bulk_create([FunctionalQuestion(
            question=rus_val,
        ) for eng_val, rus_val in values.items()])

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = u"Функциональный вопрос"
        verbose_name_plural = u"Функциональный вопрос"


class CompoundQuestion(models.Model):
    id = models.AutoField(primary_key=True)
    part = models.CharField(max_length=30, null=False, verbose_name='Составная часть в виде вопроса')

    part_eng = models.CharField(max_length=100, verbose_name='Составная часть вопроса на английском',
                                             null=False, blank=False, default='change me')

    audio = models.FileField(
        upload_to='audios/',
        validators=[
            validate_file_extension, validate_file_size
        ],
        null=True,
        blank=True,
        verbose_name='Аудио',
        help_text='до 5 мб',
    )

    audio_eng = models.FileField(
        upload_to='audios/',
        validators=[
            validate_file_extension, validate_file_size
        ],
        null=True,
        blank=True,
        verbose_name='Аудио на английском',
        help_text='до 5 мб',
    )

    @staticmethod
    def populate(values):
        CompoundQuestion.objects.bulk_create([CompoundQuestion(
            part=rus_val,
        ) for eng_val, rus_val in values.items()])

    def __str__(self):
        return self.part

    class Meta:
        verbose_name = u"Составная часть вопроса"
        verbose_name_plural = u"Составная часть вопроса"


class DefinitionQuestion(models.Model):
    id = models.AutoField(primary_key=True)
    definition = models.CharField(max_length=30, null=False, verbose_name='Определеяющий в виде вопроса')

    definition_eng = models.CharField(max_length=100, verbose_name='Определение в виде вопроса на английском',
                                               null=False, blank=False, default='change me')

    audio = models.FileField(
        upload_to='audios/',
        validators=[
            validate_file_extension, validate_file_size
        ],
        null=True,
        blank=True,
        verbose_name='Аудио',
        help_text='до 5 мб',
    )

    audio_eng = models.FileField(
        upload_to='audios/',
        validators=[
            validate_file_extension, validate_file_size
        ],
        null=True,
        blank=True,
        verbose_name='Аудио на английском',
        help_text='до 5 мб',
    )

    @staticmethod
    def populate(values):
        DefinitionQuestion.objects.bulk_create([DefinitionQuestion(
            definition=rus_val,
        ) for eng_val, rus_val in values.items()])

    def __str__(self):
        return self.definition

    class Meta:
        verbose_name = u"Определение в виде вопроса"
        verbose_name_plural = u"Определение в виде вопроса"


class SubCategory(models.Model):
    description = models.CharField(unique=True, max_length=100, verbose_name='Подкатегория')

    description_eng = models.CharField(max_length=100, verbose_name='Подкатегория на английском', null=False,
                                       blank=False, default='change me')

    audio = models.FileField(
        upload_to='audios/',
        validators=[
            validate_file_extension, validate_file_size
        ],
        null=True,
        blank=True,
        verbose_name='Аудио',
        help_text='до 5 мб',
    )

    audio_eng = models.FileField(
        upload_to='audios/',
        validators=[
            validate_file_extension, validate_file_size
        ],
        null=True,
        blank=True,
        verbose_name='Аудио на английском',
        help_text='до 5 мб',
    )

    class Meta:
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'

    def __str__(self):
        return self.description


class Quantity(models.Model):
    description = models.CharField(unique=True, max_length=50, verbose_name='Количество')

    description_eng = models.CharField(max_length=100, verbose_name='Количество на английском', null=False, blank=False,
                                    default='change me')

    audio = models.FileField(
        upload_to='audios/',
        validators=[
            validate_file_extension, validate_file_size
        ],
        null=True,
        blank=True,
        verbose_name='Аудио',
        help_text='до 5 мб',
    )

    audio_eng = models.FileField(
        upload_to='audios/',
        validators=[
            validate_file_extension, validate_file_size
        ],
        null=True,
        blank=True,
        verbose_name='Аудио на английском',
        help_text='до 5 мб',
    )

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = 'Количество'
        verbose_name_plural = 'Показатель количества'


class Game_1_obj_Manager(models.Manager):
    def random(self):
        count = self.aggregate(count=Count('id'))['count']
        random_index = randint(0, count - 1)
        return self.all()[random_index]


class Game_1_obj(models.Model):
    id = models.AutoField(primary_key=True)

    description = models.CharField(max_length=100, verbose_name='Название')
    description_eng = models.CharField(max_length=100, verbose_name='Название на английском', null=False, blank=False,
                                       default='change me')

    image = models.ImageField(upload_to="images/", null=True, verbose_name='Загрузить изображение', help_text='до 5 мб')

    # audio = models.FileField(
    #     upload_to='audios/',
    #     validators=[
    #         validate_file_extension, validate_file_size
    #     ],
    #     null=True,
    #     blank=True,
    #     verbose_name='Аудио',
    #     help_text='до 5 мб',
    # )
    #
    # audio_eng = models.FileField(
    #     upload_to='audios/',
    #     validators=[
    #         validate_file_extension, validate_file_size
    #     ],
    #     null=True,
    #     blank=True,
    #     verbose_name='Аудио на английском',
    #     help_text='до 5 мб',
    # )

    material = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name='Материал')

    form = models.ForeignKey(Form, on_delete=models.CASCADE, verbose_name='Форма')

    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')

    quantity = models.ForeignKey(Quantity, on_delete=models.CASCADE, verbose_name='Количество', null=True, blank=True)

    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, verbose_name='Подкатегория', null=True, blank=True)

    functional_question = models.ForeignKey(FunctionalQuestion, on_delete=models.CASCADE,
                                            verbose_name='Функциональный вопрос')

    compound_question = models.ForeignKey(CompoundQuestion, on_delete=models.CASCADE,
                                          verbose_name='Составная часть вопроса')

    definition_question = models.ForeignKey(DefinitionQuestion, on_delete=models.CASCADE,
                                            verbose_name='Определение в виде вопроса')

    color = models.ForeignKey(Color, on_delete=models.CASCADE,
                              verbose_name='Цвет')

    last_changed = models.DateTimeField(auto_now_add=True, blank=True, null=True,
                                        verbose_name='Последнее время изменений')

    def save(self, *args, **kwargs):
        if self.color == 'не указно':
            self.description = '{}'.format(self.sub_category)
        else:
            self.description = '{}+{}'.format(self.color, self.sub_category)
        self.last_changed = timezone.now()
        return super(Game_1_obj, self).save(*args, **kwargs)

    objects = Game_1_obj_Manager()

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = u"Объект игры № 1"
        verbose_name_plural = u"Массив изображений № 1"


class Game_2_Obj_Level_1(models.Model):
    description = models.CharField(max_length=100, verbose_name='Название группы')
    description_eng = models.CharField(max_length=100, verbose_name='Название группы на английском',
                                       default='change me')

    image_1 = models.ImageField(upload_to="images/", null=False, verbose_name='Загрузить изображение №1',
                                help_text='до 5 мб')
    image_2 = models.ImageField(upload_to="images/", null=False, verbose_name='Загрузить изображение №2',
                                help_text='до 5 мб')

    last_changed = models.DateTimeField(auto_now_add=True, blank=True, null=True,
                                        verbose_name='Последнее время изменений')

    def save(self, *args, **kwargs):
        self.last_changed = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = u"Объект игры № 4 (уровень 1)"
        verbose_name_plural = u"Группы изображений для уровня № 1"


class Game_2_Obj_Level_2(models.Model):
    description = models.CharField(max_length=100, verbose_name='Название группы')
    description_eng = models.CharField(max_length=100, verbose_name='Название группы на английском',
                                       default='change me')

    image_1 = models.ImageField(upload_to="images/", null=False, verbose_name='Загрузить изображение №1',
                                help_text='до 5 мб')
    image_2 = models.ImageField(upload_to="images/", null=False, verbose_name='Загрузить изображение №2',
                                help_text='до 5 мб')
    image_3 = models.ImageField(upload_to="images/", null=False, verbose_name='Загрузить изображение №3',
                                help_text='до 5 мб')

    last_changed = models.DateTimeField(auto_now_add=True, blank=True, null=True,
                                        verbose_name='Последнее время изменений')

    def save(self, *args, **kwargs):
        self.last_changed = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = u"Объект игры № 4 (уровень 2)"
        verbose_name_plural = u"Группы изображений для уровня № 2"


class Game_2_Obj_Level_3(models.Model):
    description = models.CharField(max_length=100, verbose_name='Название группы')
    description_eng = models.CharField(max_length=100, verbose_name='Название группы на английском',
                                       default='change me')

    image_1 = models.ImageField(upload_to="images/", null=False, verbose_name='Загрузить изображение №1',
                                help_text='до 5 мб')
    image_2 = models.ImageField(upload_to="images/", null=False, verbose_name='Загрузить изображение №2',
                                help_text='до 5 мб')
    image_3 = models.ImageField(upload_to="images/", null=False, verbose_name='Загрузить изображение №3',
                                help_text='до 5 мб')
    image_4 = models.ImageField(upload_to="images/", null=False, verbose_name='Загрузить изображение №4',
                                help_text='до 5 мб')
    image_5 = models.ImageField(upload_to="images/", null=False, verbose_name='Загрузить изображение №5',
                                help_text='до 5 мб')

    last_changed = models.DateTimeField(auto_now_add=True, blank=True, null=True,
                                        verbose_name='Последнее время изменений')

    def save(self, *args, **kwargs):
        self.last_changed = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = u"Объект игры № 4 (уровень 3)"
        verbose_name_plural = u"Группы изображений для уровня № 3"


class Game_3_Obj(models.Model):
    image_1 = models.ImageField(upload_to="images/", null=False, verbose_name='Загрузить изображение',
                                help_text='до 5 мб')
    verb = models.CharField(max_length=100, verbose_name='Глагол', null=False, blank=False)
    verb_eng = models.CharField(max_length=100, verbose_name='Глагол на английском', null=False, blank=False,
                                       default='change me')

    last_changed = models.DateTimeField(auto_now_add=True, blank=True, null=True,
                                        verbose_name='Последнее время изменений')

    audio = models.FileField(
        upload_to='audios/',
        validators=[
            validate_file_extension, validate_file_size
        ],
        null=True,
        blank=True,
        verbose_name='Аудио',
        help_text='до 5 мб',
    )

    audio_eng = models.FileField(
        upload_to='audios/',
        validators=[
            validate_file_extension, validate_file_size
        ],
        null=True,
        blank=True,
        verbose_name='Аудио на английском',
        help_text='до 5 мб',
    )

    def save(self, *args, **kwargs):
        self.last_changed = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.verb

    class Meta:
        verbose_name = u"Объект игры № 5 "
        verbose_name_plural = u"Массив изображений № 3"


class Rule(models.Model):
    description = models.CharField(max_length=100, blank=True, null=True, verbose_name='Описание')

    level = models.IntegerField(
        "Уровень игры",
        null=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
        help_text='Целочисленное значение от 1 до 5'
    )

    game = models.IntegerField(
        "Номер игры",
        null=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
        help_text='Целочисленное значение от 1 до 5'
    )

    completely_identical = models.BooleanField(
        default=True,
        verbose_name='Точное совпадение',
        help_text='Убрерите галочку, если точное совпадение не требуется'
    )

    completion_criterion = models.IntegerField(
        "Количество для завершения уровня",
        null=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(20),
        ],
        help_text='Целочисленное значение от 1 до 20'
    )

    count_up = models.IntegerField(
        "Количество картинок сверху",
        null=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(20),
        ],
        help_text='Целочисленное значение от 1 до 20'
    )

    count_bottom = models.IntegerField(
        "Количество картинок снизу",
        null=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(20),
        ],
        help_text='Целочисленное значение от 1 до 20'
    )

    class Meta:
        verbose_name = u"Правило"
        verbose_name_plural = u"Правила"

        unique_together = (
            ("game", "level"),
        )


class ImageUpload(models.Model):
    datafile = models.ImageField(upload_to="images/")
