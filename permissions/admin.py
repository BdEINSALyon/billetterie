from django.contrib import admin

from permissions import models


@admin.register(models.AzureGroup)
class AzureGroupAdmin(admin.ModelAdmin):
    pass


@admin.register(models.CheckLock)
class CheckLockAdmin(admin.ModelAdmin):
    pass
