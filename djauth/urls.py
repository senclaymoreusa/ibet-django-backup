"""djauth URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

# djauth/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
import xadmin

xadmin.autodiscover()

# from xadmin.plugins import xversion
# xversion.register_models()
    


urlpatterns = [
#    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('', RedirectView.as_view(url='/admin/')),
    path('admin/', admin.site.urls),
    path('xadmin/', xadmin.site.urls),
    path('users/', include('users.urls')),
    path('operation/', include('operation.urls')),
    path('games/', include('games.urls')),
    path('bonus/', include('bonus.urls')),
    path('system/', include('system.urls')),
    path('users/', include('django.contrib.auth.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('accounting/', include('accounting.urls')),
    path('api-auth/', include('rest_framework.urls')),   # Stephen
    path('rest-auth/', include('rest_auth.urls')),         # Stephen
    path('rest-auth/registration/', include('rest_auth.registration.urls'))    # Stephen
]

import games.views.kygameviews as kyviews

kyviews.getBets(repeat=300, repeat_until=None)

import games.views.onebookviews as onebookviews

onebookviews.getBetDetail(repeat=300,repeat_until=None)

# Use static() to add url mapping to serve static files during development (only)
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

urlpatterns+= static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


#Add Django site authentication urls (for login, logout, password management)
urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


#Add ckeditor urls
urlpatterns += [
    path('ckeditor/', include('ckeditor_uploader.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
