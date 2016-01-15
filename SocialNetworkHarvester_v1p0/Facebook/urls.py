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
    url(r'^/$', facebookBase),
    url(r'^/user/(?P<FBUserScreenName>[\w\.]+)$', fbUserView),
    url(r'^/post/(?P<FBPostId>[\w\.]+)$', fbPostView),
    url(r'^/comment/(?P<FBCommentId>\d+)$', fbCommentView),



    # ajax
    url(r'FBUserTable/(?P<aspiraUserId>\d+)', ajaxFbUserTable),
    url(r'FBPostTable/(?P<aspiraUserId>\d+)', ajaxFbPostTable),
    url(r'FBCommentTable/(?P<aspiraUserId>\d+)', ajaxFbCommentTable),
]
