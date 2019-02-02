import logging

from django.apps import apps
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.utils.html import mark_safe

from . import models

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

    search_fields = ('child__name__icontains', )
    list_display = ('child', 'game', 'level', 'correct_percentage')

    def has_add_permission(self, request):
        if not request.user.is_superuser:
            return False
        return True

    def has_change_permission(self, request, obj=None):
        if not request.user.is_superuser:
            return False
        return True

    def has_module_permission(self, request):
        if not request.user.is_superuser:
            return False
        return True

    def has_view_permission(self, request, obj=None):
        if not request.user.is_superuser:
            return False
        return True

    def check_perm(self, user_obj):
        return True


@admin.register(models.Form)
class FormAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):

    search_fields = ('form', )

    def check_perm(self, user_obj):
        return True


@admin.register(models.Category)
class CategoryAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):

    search_fields = ('category', )

    def check_perm(self, user_obj):
        return True


@admin.register(models.Color)
class ColorAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):

    search_fields = ('color', 'description')

    def check_perm(self, user_obj):
        return True


@admin.register(models.CompoundQuestion)
class CompoundQuestionAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):

    search_fields = ('part', )

    def check_perm(self, user_obj):
        return True


@admin.register(models.DefinitionQuestion)
class DefinitionQuestionAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):

    search_fields = ('definition', )

    def check_perm(self, user_obj):
        return True


@admin.register(models.FunctionalQuestion)
class FunctionalQuestionAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):

    search_fields = ('question', )

    def check_perm(self, user_obj):
        return True


@admin.register(models.Material)
class MaterialAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):

    search_fields = ('material', )

    def check_perm(self, user_obj):
        return True


@admin.register(models.SubCategory)
class SubCategoryAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):

    search_fields = ('description', )

    def check_perm(self, user_obj):
        return True


@admin.register(models.Quantity)
class QuantityAdmin(StaffRequiredAdminMixin, admin.ModelAdmin):

    search_fields = ('description', )

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

    def check_perm(self, user_obj):
        return True


@admin.register(models.Game_2_Obj_Level_2)
class Game2Level2Admin(StaffRequiredAdminMixin, admin.ModelAdmin):
    search_fields = ('description',)
    exclude = ('last_changed',)

    def check_perm(self, user_obj):
        return True


@admin.register(models.Game_2_Obj_Level_3)
class Game2Level3Admin(StaffRequiredAdminMixin, admin.ModelAdmin):
    search_fields = ('description',)
    exclude = ('last_changed',)

    def check_perm(self, user_obj):
        return True


@admin.register(models.Game_3_Obj)
class Game3(StaffRequiredAdminMixin, admin.ModelAdmin):
    search_fields = ('verb', )
    exclude = ('last_changed',)

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
        'category',
        'sub_category',
        'color',
        'material',
        'quantity',
        'form',
        'functional_question',
        'compound_question',
        'definition_question',
        'description_eng'
    ]

    readonly_fields = ['bold_description', 'pic', 'hint_audio',]
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
            '<audio src="{url}" controls>Your browser does not support the audio element.</audio>'
                .format(url=obj.audio.url)
        )

    hint_audio.short_description = 'Воспроизвести аудиоподсказку'
    hint_audio.allow_tags = True

    def get_fields(self, request, obj=None):
        if obj:
            return [self.fields[0]] + ['pic'] +\
                   [self.fields[1]] + ['hint_audio'] +\
                   self.fields[2:] + ['bold_description']

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
