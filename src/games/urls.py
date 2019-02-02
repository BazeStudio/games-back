from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.generic.base import RedirectView

from rest_framework_swagger.views import get_swagger_view
from games.api import urls as api_urls
from . import settings
schema_view = get_swagger_view(title='API Игры')


admin.site.index_template = 'entities/admin.html'
admin.autodiscover()

urlpatterns = [
    url(r'^api/v1/', include('rest_auth.urls')),
    path('api/v1/', include(api_urls.router.urls), name='change_me'),
    path('api/v1/', include(api_urls.urlpatterns), name='games'),
    url(r'^api/v1/registration/', include('rest_auth.registration.urls')),
    path('admin/', admin.site.urls),
    url('admin/games/', RedirectView.as_view(url='/admin')),
    url(r'swagger/', schema_view),
    url(r'^$', RedirectView.as_view(url='/admin')),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) +\
              static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.autodiscover()

# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns = [
#         url('__debug__/', include(debug_toolbar.urls)),
#     ] + urlpatterns
