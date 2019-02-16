import logging

from django.apps import apps
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.utils.html import mark_safe
from io import StringIO
import csv
from django.http import HttpResponseRedirect
from django.conf.urls import url
from . import models
from django.contrib import messages
from django.core.mail import EmailMessage
import re

logger = logging.getLogger(__name__)


admin.site.site_header = "Админ-панель Kit4Kid"
admin.site.site_title = "Портал Админ-панель Kit4Kid"
admin.site.index_title = "Добро пожаловать в админ-панель Kit4Kid"

admin.site.unregister(Site)
admin.site.unregister(Group)


apps.get_app_config('games').verbose_name = ''


class StaffRequiredAdminMixin(object):

    def check_perm(self, user_obj):
        if not user_obj.is_superuser:
            return False
        return True

    def has_add_permission(self, request):
        return self.check_perm(request.user)

    def has_change_permission(self, request, obj=None):
        return self.check_perm(request.user)

    def has_delete_permission(self, request, obj=None):
        return self.check_perm(request.user)

    def has_module_permission(self, request):
        return self.check_perm(request.user)

    def has_view_permission(self, request, obj=None):
        return self.check_perm(request.user)

    def has_view_or_change_permission(self, request, obj=None):
        return self.check_perm(request.user)


@admin.register(models.User)
class UserAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):

    change_form_template = 'entities/change_user_form.html'

    fields = [
        'username',
        'email',
        'phone',
        'is_active',
        'date_joined',
        'name',
        'surname',
    ]

    readonly_fields = ['link_to_child', 'date_joined']

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            # URL for button in template
            url('load/', self.send_stats),
        ]
        return my_urls + urls

    def send_stats(self, request, **kwargs):
        logger.info("Retrieve command for send statistic")
        if request.method == "GET":

            entered_email = request.GET['email']
            if re.match("^.+@(\[?)[a-zA-Z0-9-.]+.([a-zA-Z]{2,3}|[0-9]{1,3})(]?)$", entered_email) is None:
                messages.add_message(request, messages.ERROR,
                                     'Неверный почтовый адрес')
                return HttpResponseRedirect('../')

            object_id = request.path.split('/')[4]
            user = models.User.objects.get(pk=int(object_id))
            if entered_email:
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

                mail = EmailMessage('Статистика Kit-4-Kid',
                                    'Здравствуйте.\n\nСтатистика игр по Вашим детям:\nИгра 1 - Сопоставления,\nИгра 2 - Различения,\nИгра 3 - Категории,\nИгра 4 - Последовательности,\nИгра 5 - Глаголы\n\n\nС уважением,\nадминистрация Kit-4-Kid',
                                    'info@kit-4-kid', (entered_email,))
                mail.attach('statistics.csv', attachment_csv_file.getvalue(), 'text/csv')
                mail.send(fail_silently=True)

                messages.add_message(request, messages.INFO,
                                     'Статистика успешно отправлена')
            else:
                messages.add_message(request, messages.ERROR,
                                     'Почта не указана')

        return HttpResponseRedirect('../')

    def link_to_child(self, obj):
        if obj:
            # noinspection PyUnresolvedReferences
            childs = models.Child.objects.filter(parent=obj.id)
            child_tags = ''
            for num, child in enumerate(childs):
                child_tags += '<p><a href="/admin/games/child/%s/change/" target="_blank">%s</a></p>'\
                                     % (child.id, child.name)

            if child_tags != '':
                return mark_safe(child_tags)

            return 'Отсутствуют'

    link_to_child.allow_tags = True
    link_to_child.short_description = 'Дети'

    def get_queryset(self, request):
        qs = super(UserAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(is_staff=False).filter(is_superuser=False)

    def has_add_permission(self, request):
        if not request.user.is_superuser:
            return False
        return True

    def has_change_permission(self, request, obj=None):
        if not request.user.is_superuser:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        if not request.user.is_superuser:
            return False
        return True

    def check_perm(self, user_obj):
        return True

    def get_fields(self, request, obj=None):
        fields = self.fields
        if obj:
            if not request.user.is_superuser and 'is_active' in fields:
                fields.remove('is_active')
            return fields + ['link_to_child']

        return fields


@admin.register(models.Statistic)
class StatisticAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):

    search_fields = ('child__name__icontains',)
    list_display = ('child', 'get_parent', 'game', 'level', 'correct_percentage',)

    def get_parent(self, obj):
        if obj.child.parent.name and obj.child.parent.surname:
            return obj.child.parent.surname + ' ' + obj.child.parent.name
        elif obj.child.parent.name and not obj.child.parent.surname:
            return obj.child.parent.name
        else:
            return 'Отсувует'

    def get_search_results(self, request, queryset, search_term):
        search_term = search_term.strip()
        qs, use_distinct = super().get_search_results(request, queryset, search_term)
        if len(qs) != 0:
            return qs, use_distinct
        else:
            count_spaces = search_term.count(' ')
            if count_spaces == 2:
                surname, name, name_child = search_term.split(' ')
                qs = models.Statistic.objects.filter(child__parent__name=name,child__name=name_child)

                if len(qs) != 0:
                    return qs, False
                else:
                    qs = models.Statistic.objects.filter(child__parent__name=name_child, child__parent__surname=name,
                                                         child__name=surname)
                    return qs, False
            elif count_spaces == 1:
                surname, name = search_term.split(' ', 1)
                return models.Statistic.objects.filter(child__parent__name=name, child__parent__surname=surname), False
            else:
                return qs, use_distinct

    get_parent.short_description = 'Родитель'
    get_parent.admin_order_field = 'child__parent__name'

    def has_add_permission(self, request):
        if not request.user.is_superuser:
            return False
        return True

    def has_change_permission(self, request, obj=None):
        if not request.user.is_superuser:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        if not request.user.is_superuser:
            return False
        return True

    def check_perm(self, user_obj):
        return True


@admin.register(models.Form)
class FormAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):

    search_fields = ('form', )

    readonly_fields = ['hint_audio', 'hint_audio_eng']

    def hint_audio(self, obj):
        if not obj.audio:
            return 'Отсутствует'

        return mark_safe(
            '<audio src="{url}" controls>Your browser does not support the audio element.</audio>'
                .format(url=obj.audio.url)
        )

    hint_audio.short_description = 'Воспроизвести аудиоподсказку'
    hint_audio.allow_tags = True

    def hint_audio_eng(self, obj):
        if not obj.audio_eng:
            return 'Отсутствует'

        return mark_safe(
            '<audio src="{url}" controls>Your browser does not support the audio element.</audio>'
                .format(url=obj.audio_eng.url)
        )

    hint_audio_eng.short_description = 'Воспроизвести аудиоподсказку на английском'
    hint_audio_eng.allow_tags = True

    def check_perm(self, user_obj):
        return True


@admin.register(models.Category)
class CategoryAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):

    search_fields = ('category', )

    readonly_fields = ['hint_audio', 'hint_audio_eng']

    def hint_audio(self, obj):
        if not obj.audio:
            return 'Отсутствует'

        return mark_safe(
            '<audio src="{url}" controls>Your browser does not support the audio element.</audio>'
                .format(url=obj.audio.url)
        )

    hint_audio.short_description = 'Воспроизвести аудиоподсказку'
    hint_audio.allow_tags = True

    def hint_audio_eng(self, obj):
        if not obj.audio_eng:
            return 'Отсутствует'

        return mark_safe(
            '<audio src="{url}" controls>Your browser does not support the audio element.</audio>'
                .format(url=obj.audio_eng.url)
        )

    hint_audio_eng.short_description = 'Воспроизвести аудиоподсказку на английском'
    hint_audio_eng.allow_tags = True

    def check_perm(self, user_obj):
        return True


@admin.register(models.Color)
class ColorAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):

    search_fields = ('color', 'description')

    readonly_fields = ['hint_audio', 'hint_audio_eng']

    def hint_audio(self, obj):
        if not obj.audio:
            return 'Отсутствует'

        return mark_safe(
            '<audio src="{url}" controls>Your browser does not support the audio element.</audio>'
                .format(url=obj.audio.url)
        )

    hint_audio.short_description = 'Воспроизвести аудиоподсказку'
    hint_audio.allow_tags = True

    def hint_audio_eng(self, obj):
        if not obj.audio_eng:
            return 'Отсутствует'

        return mark_safe(
            '<audio src="{url}" controls>Your browser does not support the audio element.</audio>'
                .format(url=obj.audio_eng.url)
        )

    hint_audio_eng.short_description = 'Воспроизвести аудиоподсказку на английском'
    hint_audio_eng.allow_tags = True

    def check_perm(self, user_obj):
        return True


@admin.register(models.CompoundQuestion)
class CompoundQuestionAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):

    search_fields = ('part', )

    readonly_fields = ['hint_audio', 'hint_audio_eng']

    def hint_audio(self, obj):
        if not obj.audio:
            return 'Отсутствует'

        return mark_safe(
            '<audio src="{url}" controls>Your browser does not support the audio element.</audio>'
                .format(url=obj.audio.url)
        )

    hint_audio.short_description = 'Воспроизвести аудиоподсказку'
    hint_audio.allow_tags = True

    def hint_audio_eng(self, obj):
        if not obj.audio_eng:
            return 'Отсутствует'

        return mark_safe(
            '<audio src="{url}" controls>Your browser does not support the audio element.</audio>'
                .format(url=obj.audio_eng.url)
        )

    hint_audio_eng.short_description = 'Воспроизвести аудиоподсказку на английском'
    hint_audio_eng.allow_tags = True

    def check_perm(self, user_obj):
        return True


@admin.register(models.DefinitionQuestion)
class DefinitionQuestionAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):

    search_fields = ('definition', )

    readonly_fields = ['hint_audio', 'hint_audio_eng']

    def hint_audio(self, obj):
        if not obj.audio:
            return 'Отсутствует'

        return mark_safe(
            '<audio src="{url}" controls>Your browser does not support the audio element.</audio>'
                .format(url=obj.audio.url)
        )

    hint_audio.short_description = 'Воспроизвести аудиоподсказку'
    hint_audio.allow_tags = True

    def hint_audio_eng(self, obj):
        if not obj.audio_eng:
            return 'Отсутствует'

        return mark_safe(
            '<audio src="{url}" controls>Your browser does not support the audio element.</audio>'
                .format(url=obj.audio_eng.url)
        )

    hint_audio_eng.short_description = 'Воспроизвести аудиоподсказку на английском'
    hint_audio_eng.allow_tags = True

    def check_perm(self, user_obj):
        return True


@admin.register(models.FunctionalQuestion)
class FunctionalQuestionAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):

    search_fields = ('question', )

    readonly_fields = ['hint_audio', 'hint_audio_eng']

    def hint_audio(self, obj):
        if not obj.audio:
            return 'Отсутствует'

        return mark_safe(
            '<audio src="{url}" controls>Your browser does not support the audio element.</audio>'
                .format(url=obj.audio.url)
        )

    hint_audio.short_description = 'Воспроизвести аудиоподсказку'
    hint_audio.allow_tags = True

    def hint_audio_eng(self, obj):
        if not obj.audio_eng:
            return 'Отсутствует'

        return mark_safe(
            '<audio src="{url}" controls>Your browser does not support the audio element.</audio>'
                .format(url=obj.audio_eng.url)
        )

    hint_audio_eng.short_description = 'Воспроизвести аудиоподсказку на английском'
    hint_audio_eng.allow_tags = True

    def check_perm(self, user_obj):
        return True


@admin.register(models.Material)
class MaterialAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):

    search_fields = ('material', )

    readonly_fields = ['hint_audio', 'hint_audio_eng']

    def hint_audio(self, obj):
        if not obj.audio:
            return 'Отсутствует'

        return mark_safe(
            '<audio src="{url}" controls>Your browser does not support the audio element.</audio>'
                .format(url=obj.audio.url)
        )

    hint_audio.short_description = 'Воспроизвести аудиоподсказку'
    hint_audio.allow_tags = True

    def hint_audio_eng(self, obj):
        if not obj.audio_eng:
            return 'Отсутствует'

        return mark_safe(
            '<audio src="{url}" controls>Your browser does not support the audio element.</audio>'
                .format(url=obj.audio_eng.url)
        )

    hint_audio_eng.short_description = 'Воспроизвести аудиоподсказку на английском'
    hint_audio_eng.allow_tags = True

    def check_perm(self, user_obj):
        return True


@admin.register(models.SubCategory)
class SubCategoryAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):

    search_fields = ('description', )

    readonly_fields = ['hint_audio', 'hint_audio_eng']

    def hint_audio(self, obj):
        if not obj.audio:
            return 'Отсутствует'

        return mark_safe(
            '<audio src="{url}" controls>Your browser does not support the audio element.</audio>'
                .format(url=obj.audio.url)
        )

    hint_audio.short_description = 'Воспроизвести аудиоподсказку'
    hint_audio.allow_tags = True

    def hint_audio_eng(self, obj):
        if not obj.audio_eng:
            return 'Отсутствует'

        return mark_safe(
            '<audio src="{url}" controls>Your browser does not support the audio element.</audio>'
                .format(url=obj.audio_eng.url)
        )

    hint_audio_eng.short_description = 'Воспроизвести аудиоподсказку на английском'
    hint_audio_eng.allow_tags = True

    def check_perm(self, user_obj):
        return True


@admin.register(models.Quantity)
class QuantityAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):

    search_fields = ('description', )

    readonly_fields = ['hint_audio', 'hint_audio_eng']

    def hint_audio(self, obj):
        if not obj.audio:
            return 'Отсутствует'

        return mark_safe(
            '<audio src="{url}" controls>Your browser does not support the audio element.</audio>'
                .format(url=obj.audio.url)
        )

    hint_audio.short_description = 'Воспроизвести аудиоподсказку'
    hint_audio.allow_tags = True

    def hint_audio_eng(self, obj):
        if not obj.audio_eng:
            return 'Отсутствует'

        return mark_safe(
            '<audio src="{url}" controls>Your browser does not support the audio element.</audio>'
                .format(url=obj.audio_eng.url)
        )

    hint_audio_eng.short_description = 'Воспроизвести аудиоподсказку на английском'
    hint_audio_eng.allow_tags = True

    def check_perm(self, user_obj):
        return True


@admin.register(models.Rule)
class RuleAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):
    list_filter = ['game']
    list_display = ['game', 'level', 'description']

    staff_fields = ('description', 'game', 'level')
    superuser_fields = ('',)

    # def has_add_permission(self, request):
    #     if not request.user.is_superuser:
    #         return False
    #     return True
    #
    # def has_change_permission(self, request, obj=None):
    #     return True
    #
    # def has_delete_permission(self, request, obj=None):
    #     if not request.user.is_superuser:
    #         return False
    #     return True
    #
    # def has_module_permission(self, request):
    #     return True
    #
    # def has_view_permission(self, request, obj=None):
    #     return True

    def has_view_or_change_permission(self, request, obj=None):
        return True

    def get_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return self.staff_fields
        return super().get_fields(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            staff_read_fields = ('game', 'level', )
            return staff_read_fields

        return super().get_readonly_fields(request, obj)


@admin.register(models.Game_2_Obj_Level_1)
class Game2Level1Admin(StaffRequiredAdminMixin, admin.ModelAdmin):
    search_fields = ('description', )
    exclude = ('last_changed',)

    readonly_fields = ['pic_1', 'pic_2']

    def pic_1(self, obj):
        if obj and obj.image_1:
            return mark_safe(
                '<img src="{url}" width="{width}" height={height} />'.format(
                    url=obj.image_1.url,
                    width=obj.image_1.width / 2,
                    height=obj.image_1.height / 2,
                )
            )
        return 'Отсутствует'

    pic_1.short_description = 'Изображение 1'
    pic_1.allow_tags = True

    def pic_2(self, obj):
        if obj and obj.image_2:
            return mark_safe(
                '<img src="{url}" width="{width}" height={height} />'.format(
                    url=obj.image_2.url,
                    width=obj.image_2.width / 2,
                    height=obj.image_2.height / 2,
                )
            )
        return 'Отсутствует'

    pic_2.short_description = 'Изображение 2'
    pic_2.allow_tags = True

    def check_perm(self, user_obj):
        return True


@admin.register(models.Game_2_Obj_Level_2)
class Game2Level2Admin(StaffRequiredAdminMixin, admin.ModelAdmin):
    search_fields = ('description',)
    exclude = ('last_changed',)

    readonly_fields = ['pic_1', 'pic_2', 'pic_3']

    def pic_1(self, obj):
        if obj and obj.image_1:
            return mark_safe(
                '<img src="{url}" width="{width}" height={height} />'.format(
                    url=obj.image_1.url,
                    width=obj.image_1.width / 2,
                    height=obj.image_1.height / 2,
                )
            )
        return 'Отсутствует'

    pic_1.short_description = 'Изображение 1'
    pic_1.allow_tags = True

    def pic_2(self, obj):
        if obj and obj.image_2:
            return mark_safe(
                '<img src="{url}" width="{width}" height={height} />'.format(
                    url=obj.image_2.url,
                    width=obj.image_2.width / 2,
                    height=obj.image_2.height / 2,
                )
            )
        return 'Отсутствует'

    pic_2.short_description = 'Изображение 2'
    pic_2.allow_tags = True

    def pic_3(self, obj):
        if obj and obj.image_3:
            return mark_safe(
                '<img src="{url}" width="{width}" height={height} />'.format(
                    url=obj.image_3.url,
                    width=obj.image_3.width / 2,
                    height=obj.image_3.height / 2,
                )
            )
        return 'Отсутствует'

    pic_3.short_description = 'Изображение 3'
    pic_3.allow_tags = True

    def check_perm(self, user_obj):
        return True


@admin.register(models.Game_2_Obj_Level_3)
class Game2Level3Admin(StaffRequiredAdminMixin, admin.ModelAdmin):
    search_fields = ('description',)
    exclude = ('last_changed',)

    readonly_fields = ['pic_1', 'pic_2', 'pic_3', 'pic_4', 'pic_5']

    def pic_1(self, obj):
        if obj and obj.image_1:
            return mark_safe(
                '<img src="{url}" width="{width}" height={height} />'.format(
                    url=obj.image_1.url,
                    width=obj.image_1.width / 2,
                    height=obj.image_1.height / 2,
                )
            )
        return 'Отсутствует'

    pic_1.short_description = 'Изображение 1'
    pic_1.allow_tags = True

    def pic_2(self, obj):
        if obj and obj.image_2:
            return mark_safe(
                '<img src="{url}" width="{width}" height={height} />'.format(
                    url=obj.image_2.url,
                    width=obj.image_2.width / 2,
                    height=obj.image_2.height / 2,
                )
            )
        return 'Отсутствует'

    pic_2.short_description = 'Изображение 2'
    pic_2.allow_tags = True

    def pic_3(self, obj):
        if obj and obj.image_3:
            return mark_safe(
                '<img src="{url}" width="{width}" height={height} />'.format(
                    url=obj.image_3.url,
                    width=obj.image_3.width / 2,
                    height=obj.image_3.height / 2,
                )
            )
        return 'Отсутствует'

    pic_3.short_description = 'Изображение 3'
    pic_3.allow_tags = True

    def pic_4(self, obj):
        if obj and obj.image_4:
            return mark_safe(
                '<img src="{url}" width="{width}" height={height} />'.format(
                    url=obj.image_4.url,
                    width=obj.image_4.width / 2,
                    height=obj.image_4.height / 2,
                )
            )
        return 'Отсутствует'

    pic_4.short_description = 'Изображение 4'
    pic_4.allow_tags = True

    def pic_5(self, obj):
        if obj and obj.image_5:
            return mark_safe(
                '<img src="{url}" width="{width}" height={height} />'.format(
                    url=obj.image_5.url,
                    width=obj.image_5.width / 2,
                    height=obj.image_5.height / 2,
                )
            )
        return 'Отсутствует'

    pic_5.short_description = 'Изображение 5'
    pic_5.allow_tags = True

    def check_perm(self, user_obj):
        return True


@admin.register(models.Game_3_Obj)
class Game3(StaffRequiredAdminMixin, admin.ModelAdmin):
    search_fields = ('verb', )
    exclude = ('last_changed',)

    readonly_fields = ['pic', 'hint_audio', 'hint_audio_eng']

    def pic(self, obj):
        if obj and obj.image_1:
            return mark_safe(
                '<img src="{url}" width="{width}" height={height} />'.format(
                    url=obj.image_1.url,
                    width=obj.image_1.width / 2,
                    height=obj.image_1.height / 2,
                )
            )
        return 'Отсутствует'

    pic.short_description = 'Изображение'
    pic.allow_tags = True

    def hint_audio(self, obj):
        if not obj.audio:
            return 'Отсутствует'

        return mark_safe(
            '<audio src="{url}" controls>Your browser does not support the audio element.</audio>'
                .format(url=obj.audio.url)
        )

    hint_audio.short_description = 'Воспроизвести аудиоподсказку'
    hint_audio.allow_tags = True

    def hint_audio_eng(self, obj):
        if not obj.audio_eng:
            return 'Отсутствует'

        return mark_safe(
            '<audio src="{url}" controls>Your browser does not support the audio element.</audio>'
                .format(url=obj.audio_eng.url)
        )

    hint_audio_eng.short_description = 'Воспроизвести аудиоподсказку на английском'
    hint_audio_eng.allow_tags = True

    def check_perm(self, user_obj):
        return True


@admin.register(models.Game_1_obj)
class Game1Admin(StaffRequiredAdminMixin, admin.ModelAdmin):
    change_list_template = 'entities/game_one_list.html'
    change_form_template = 'entities/game_one_form.html'

    search_fields = ('description', )

    fields = [
        'image',
        'audio',
        'audio_eng',
        'category',
        'sub_category',
        'color',
        'material',
        'quantity',
        'form',
        'functional_question',
        'compound_question',
        'definition_question',
        'description_eng',
    ]

    readonly_fields = ['bold_description', 'pic', 'hint_audio', 'hint_audio_eng']
    exclude = ('description', )
    list_display = ('description',
                    'category',
                    'sub_category',
                    'color',
                    'material',
                    'quantity',
                    'form',
                    'functional_question',
                    'compound_question',
                    'definition_question',
                    'description_eng',
                    )

    def bold_description(self, obj):
        return mark_safe(
            '<b>{desc}</b>'.format(desc=obj.description)
        )

    bold_description.short_description = 'Название'
    bold_description.allow_tags = True

    def pic(self, obj):
        return mark_safe(
            '<img src="{url}" width="{width}" height={height} />'.format(
                url=obj.image.url,
                width=obj.image.width / 2,
                height=obj.image.height / 2,
            )
        )

    pic.short_description = 'Изображение'
    pic.allow_tags = True

    def hint_audio(self, obj):
        if not obj.audio:
            return 'Отсутствует'

        return mark_safe(
            '<audio src="{url}" conmutrols>Your browser does not support the audio element.</audio>'
                .format(url=obj.audio.url)
        )

    hint_audio.short_description = 'Воспроизвести аудиоподсказку'
    hint_audio.allow_tags = True

    def hint_audio_eng(self, obj):
        if not obj.audio_eng:
            return 'Отсутствует'

        return mark_safe(
            '<audio src="{url}" controls>Your browser does not support the audio element.</audio>'
                .format(url=obj.audio_eng.url)
        )

    hint_audio_eng.short_description = 'Воспроизвести аудиоподсказку на английском'
    hint_audio_eng.allow_tags = True

    def get_fields(self, request, obj=None):
        if obj:
            return [self.fields[0]] + ['pic'] +\
                   [self.fields[1]] + ['hint_audio'] + \
                   [self.fields[2]] + ['hint_audio_eng'] + \
                    self.fields[3:] + ['bold_description']

        return self.fields

    def formfield_for_foreignkey(self, field, request, **kwargs):
        if field.name == "sub_category":
            kwargs["queryset"] = models.SubCategory.objects.order_by('description')

        if field.name == "image":
            kwargs["queryset"] = models.Image.objects.order_by('name')

        if field.name == "category":
            kwargs["queryset"] = models.Category.objects.order_by('category')

        if field.name == "functional_question":
            kwargs["queryset"] = models.FunctionalQuestion.objects.order_by('question')

        if field.name == "compound_question":
            kwargs["queryset"] = models.CompoundQuestion.objects.order_by('part')

        if field.name == "definition_question":
            kwargs["queryset"] = models.DefinitionQuestion.objects.order_by('definition')

        if field.name == "color":
            kwargs["queryset"] = models.Color.objects.order_by('color')

        return super(Game1Admin, self).formfield_for_foreignkey(field, request, **kwargs)

    def check_perm(self, user_obj):
        return True


@admin.register(models.Child)
class AdminChild(StaffRequiredAdminMixin, admin.ModelAdmin):

    fields = [
        'name',
        'birthday',
        'gender',
        'parent',
    ]

    list_display = ('name', 'parent', )
    search_fields = ('parent__name', 'parent__surname', )

    def get_fields(self, request, obj=None):
        if obj:
            return self.fields

        return self.fields

    def has_add_permission(self, request):
        if not request.user.is_superuser:
            return False
        return True

    def has_change_permission(self, request, obj=None):
        if not request.user.is_superuser:
            return False
        return True

    def check_perm(self, user_obj):
        return True
