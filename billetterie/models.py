from django.db import models
from django.utils.translation import ugettext_lazy as _

from ticketing.models import Event


class Billetterie(models.Model):

    event = models.ForeignKey(Event, verbose_name=_('Evènement'), related_name='entries')
    title = models.CharField(max_length=255, verbose_name=_('Nom'))
    miniature_background = models.ImageField(verbose_name=_("Miniature liste"), blank=True)
    event_header = models.ImageField(verbose_name=_("En-tête billetterie"), blank=True)
    displayed_date = models.DateTimeField()
    description = models.TextField()
    published = models.BooleanField()
    access_mode = models.CharField(choices=('Public', 'Invitation', 'Gala', 'Code'))
    entry_sold = models.ManyToManyField(Entry)
