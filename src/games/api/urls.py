from rest_framework.routers import DefaultRouter
from django.conf.urls import url

from . import views

router = DefaultRouter(trailing_slash=False)
router.register(r'child', views.ChildViewSet)
router.register(r'comments', views.CommentsViewSet)
# router.register(r'users', views.UserViewSet)

urlpatterns = [
    url(r'^users/(?P<key>[\w\d]+)/$', views.get_user, name='user_detail'),
    url(r'^users/(?P<key>[\w\d]+)/childs/$', views.get_childs, name='childs'),
    url(r'^users/(?P<key>[\w\d]+)/childs/$', views.append_child, name='childs'),
]
