from django.db import models

# Create your models here.


class AccessToken(models.Model):

    class Meta:
        app_label = "Facebook"

    _token = models.CharField(max_length=255)






def setFBToken(newToken):
    token = None
    if AccessToken.objects.count() > 1 :
        raise Exception('More than one AccessToken exists!')
    elif AccessToken.objects.count() > 0:
        token = AccessToken.objects.all()[0]
    if not token:
        token = AccessToken.objects.create()
    token._token = newToken
    token.save()



def getFBToken():
    token = None
    if AccessToken.objects.count() > 1:
        raise Exception('More than one AccessToken exists!')
    elif AccessToken.objects.count() > 0:
        token = AccessToken.objects.all()[0]
    return token._token
