from django.contrib import admin
from ticketing import models


admin.site.register(models.Event)
admin.site.register(models.Entry)
admin.site.register(models.SellLocation)
admin.site.register(models.Ticket)
admin.site.register(models.Validation)
admin.site.register(models.VALink)
admin.site.register(models.YurplanLink)
