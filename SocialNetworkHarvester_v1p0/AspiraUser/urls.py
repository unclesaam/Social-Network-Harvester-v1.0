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
from .views import *

urlpatterns = [
    url(r'^$', userDashboard),
    url(r'^(?i)login$', userLogin),
    url(r'^(?i)register', userRegister),
    url(r'^(?i)login_page$', userLoginPage),
    url(r'^(?i)logout$', userLogout),
    url(r'^(?i)settings$', userSettings),
    url(r'^(?i)edit_user_settings$', editUserSettings),
    url(r'^(?i)setUserSelection$', setUserSelection),
    url(r'^(?i)removeSelectedItems', removeSelectedItems),
    url(r'^(?i)confidentialityAgreement', confAgreement),
    url(r'^(?i)supported_browsers_list', browserList),
]
