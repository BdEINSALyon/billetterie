from django.db import models
from django.utils.translation import ugettext_lazy as _


class Event(models.Model):
    class Meta:
        verbose_name = _('Evènement')

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Entry(models.Model):
    class Meta:
        verbose_name = _('Tarif')

    name = models.CharField(max_length=255)
    price_ht = models.DecimalField(verbose_name=_('Prix HT'), decimal_places=2, max_digits=11)
    price_ttc = models.DecimalField(verbose_name=_('Prix TTC'), decimal_places=2, max_digits=11)
    event = models.ForeignKey(Event, verbose_name=_('Evènement'), related_name='entries')

    def __str__(self):
        return self.name


class SellLocation(models.Model):
    class Meta:
        verbose_name = _('Lieu de vente')
        verbose_name_plural = _('Lieux de vente')

    name = models.CharField(max_length=255)
    latitude = models.DecimalField(decimal_places=10, max_digits=13)
    longitude = models.DecimalField(decimal_places=10, max_digits=13)

    def __str__(self):
        return self.name


class Sell(models.Model):
    class Meta:
        verbose_name = _('Vente')

    payment_methods = (
        ('CB', _('Carte Bancaire')),
        ('ESP', _('Espèces')),
        ('CHQ', _('Chèque')),
        ('VIR', _('Virement Bancaire')),
    )
    email = models.EmailField()
    payment_method = models.CharField(max_length=3, choices=payment_methods)
    location = models.ForeignKey(SellLocation, related_name='sells')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    refunded = models.BooleanField(default=False)

    def id(self):
        return "{}-{}".format(self.payment_method, self.pk)

    def __str__(self):
        return "Vente #{}".format(self.id())


class Ticket(models.Model):
    class Meta:
        verbose_name = _('Billet')

    available_ticket_types = (
        ('classic', _('Classique')),
        ('yurplan', 'Yurplan'),
        ('va', 'Carte VA')
    )
    entry = models.ForeignKey(Entry, verbose_name=_('Tarif'), related_name='tickets')
    email = models.EmailField()
    ticket_type = models.CharField(max_length=50, choices=available_ticket_types)
    first_name = models.CharField(max_length=255, verbose_name=_('Prénom'))
    last_name = models.CharField(max_length=255, verbose_name=_('Nom'))
    sell = models.ForeignKey(Sell, related_name='tickets')

    def id(self):
        return "{}-{}-{}".format(self.entry.event.pk, self.sell.pk, self.pk)

    def __str__(self):
        return "Ticket #{}".format(self.id())


class VALink(models.Model):
    class Meta:
        verbose_name = _('Carte VA')

    ticket = models.ForeignKey(Ticket, related_name='va', limit_choices_to={'type': 'va'})
    va_id = models.IntegerField(verbose_name=_('Numéro d\'adhérant'))
    card_id = models.CharField(max_length=15)

    def __str__(self):
        return "VA #{}".format(self.va_id)


class YurplanLink(models.Model):
    class Meta:
        verbose_name = _('Lien Yurplan')

    yurplan_id = models.CharField(max_length=70, verbose_name=_('Numéro de billet yurplan'))
    yurplan_event = models.IntegerField(verbose_name=_('Evènement Yurplan'))
    ticket = models.ForeignKey(Ticket, related_name='yurplan', limit_choices_to={'type': 'yurplan'})

    def __str__(self):
        return self.yurplan_id


class Validation(models.Model):
    class Meta:
        verbose_name = _('Validation')

    created_at = models.DateTimeField(auto_now_add=True)
    ticket = models.ForeignKey(Ticket, related_name='validation_entry')

    def __str__(self):
        return "Validation #{}".format(self.ticket.id())

