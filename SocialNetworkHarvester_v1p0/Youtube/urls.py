"""SocialNetworkHarvester_v1p0 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from .views.pages import *
from .views.ajax import ajaxBase
from .views.forms import formBase

urlpatterns = [
    url(r'^$', youtubeBase),
    url(r'channel/(?P<identifier>[\w\.]+)?', channelBase),
    url(r'video/(?P<identifier>[\w\.]+)?', videoBase),
    url(r'comment/(?P<identifier>[\w\.]+)?', commentBase),
    url(r'ajax', ajaxBase),
    url(r'forms/(?P<formName>[\w\.]+)', formBase),
]
