from django.contrib.auth import models as auth_models
from account import models as account_models
from django.db import models


class AzureGroup(models.Model):

    group = models.ForeignKey(auth_models.Group)
    azure_id = models.CharField(max_length=100, choices=())

    def check_user(self, user):
        for token in account_models.OAuthToken.objects.filter(user=user):
            if token.service.name == 'microsoft':
                # Check Key to microsoft
                microsoft = token.service.provider


class CheckLock(models.Model):

    user = models.ForeignKey(auth_models.User)
    event = models.ForeignKey('ticketing.Event')
    created_at = models.DateTimeField(auto_now_add=True)

