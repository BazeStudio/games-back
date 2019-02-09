from rest_framework.routers import DefaultRouter
from django.conf.urls import url

from . import views

router = DefaultRouter(trailing_slash=False)
# router.register(r'child', views.ChildViewSet)
router.register(r'comments', views.CommentsViewSet)
router.register(r'statistics', views.StatisticViewSet)
router.register(r'files', views.FileUploadViewSet)

urlpatterns = [
    url(r'^users/(?P<key>[\w\d]+)/$', views.get_user, name='user_detail'),
    url(r'^users/reset_password', views.reset_password, name='change_password'),
    url(r'^users/(?P<key>[\w\d]+)/childs/$', views.child, name='child'),
    url(r'^users/(?P<key>[\w\d]+)/change_password', views.change_password, name='child'),
    url(r'^objects/first/(?P<date>[\d-]+)/$', views.get_first_game_objects_for_update, name='first_array'),
    url(r'^objects/second/1/(?P<date>[\d-]+)/$', views.get_second_array_first_level, name='second_array_level_1'),
    url(r'^objects/second/2/(?P<date>[\d-]+)/$', views.get_second_array_second_level, name='second_array_level_2'),
    url(r'^objects/second/3/(?P<date>[\d-]+)/$', views.get_second_array_third_level, name='second_array_level_3'),
    url(r'^objects/third/(?P<date>[\d-]+)/$', views.get_third_array, name='third_array'),
    url(r'^comments/by_child/(?P<child_id>[\d]+)/$', views.get_child_comments, name='child_comments'),
    url(r'^statistics/by_child/(?P<child_id>[\d]+)/$', views.get_child_statistics, name='child_statistics'),
    url(r'^check_update/(?P<date>[\d\w\-:]+)/$', views.check_update, name='check_update'),
    url(r'^registration/$', views.CustomRegisterView.as_view(), name='registration'),
    url(r'^users/(?P<key>[\w\d]+)/approve/$', views.user_approve, name='approve'),
    url(r'^users/(?P<key>[\w\d]+)/email_confirmation/$', views.email_confirmation, name='email_confirmation'),
    url(r'^users/(?P<key>[\w\d]+)/send_statistics/$', views.send_statistics, name='send_statistics'),
    url(r'^users/(?P<key>[\w\d]+)/send_sms/$', views.send_sms_to_user, name='send_sms'),
    url(r'^registration/social$', views.social_registration, name='social_registration'),
    url(r'^login/social$', views.social_login, name='social_login'),
]
