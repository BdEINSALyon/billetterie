from _md5 import md5

import re
from datetime import datetime, timedelta
from django.conf import settings

from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import ugettext_lazy as _

from permissions.models import CheckLock, AzureGroup
from ticketing import security
from ticketing import yurplan
from ticketing.marsu import MarsuAPI


class Event(models.Model):
    class Meta:
        verbose_name = _('Evènement')

    name = models.CharField(max_length=255)
    ticket_background = models.ImageField(verbose_name=_("Fond d'image tickets"), blank=True)
    groups = models.ManyToManyField(Group)
    yurplan_event_id = models.IntegerField(blank=True, null=True)
    sales_opening = models.DateTimeField(default=datetime.now)
    sales_closing = models.DateTimeField(default=datetime.now)
    max_seats = models.IntegerField(default=1600, verbose_name=_('Nombre maximal de place'))
    seats_goal = models.IntegerField(default=1600)
    closed_days_count = models.IntegerField(default=13)
    logo_url = models.CharField(max_length=2500, default='http://logos.bde-insa-lyon.fr/bal/Logo_bal.png', blank=True, null=True)
    email_background_color = models.CharField(max_length=7, default='#3C121C')
    email_button_color = models.CharField(max_length=7, default='#6D1928')
    email_more_info_link = models.CharField(max_length=2500, default='http://bal.bde-insa-lyon.fr', blank=True, null=True)
    email_important_information_html = models.TextField(default='<h2  class="align-center">Informations importantes'
                                                                '</h2>'
                                                                '<p class="align-center">Ouverture des portes&nbsp;: '
                                                                '22h00</p>'
                                                                '<p class="align-center">Dernière '
                                                                'entrée&nbsp;: <b>02h30</b></p>',
                                                                blank=True, null=True)

    def can_be_managed_by(self, user):
        # Check if the user belongs to an authorized group
        if self.groups.filter(user=user).count() > 0:
            return True

        # Check if user has not be locked for that group
        if CheckLock.objects.filter(user=user, event=self,
                                    created_at__gte=datetime.now() - timedelta(hours=1)).count() > 0:
            return False

        # Check the AzureGroup for that user
        for azure_group in AzureGroup.objects.filter(group__event=self):
            if azure_group.check_user(user):
                return True

        # Disable check for one hour
        CheckLock(user=user, event=self).save()
        return False

    def load_yurplan_order(self, yurplan_order):
        order = yurplan.ApiClient().get_order(self.yurplan_event_id, yurplan_order)
        tickets = order['tickets']
        for ticket in tickets:
            if YurplanLink.objects.filter(yurplan_ticket_id=ticket['id']).count() < 1:
                ticket = yurplan.ApiClient().get_ticket(self.yurplan_event_id, ticket['id'])
                try:
                    valet_ticket = Ticket(
                        first_name=ticket['first_name'],
                        last_name=ticket['last_name'],
                        email='no-reply@yurplan.com',
                        ticket_type='yurplan',
                        entry=self.entries.get(yurplan_id=ticket['type_ticket']['id']))
                    valet_ticket.save()
                    YurplanLink(
                        event_id=self.yurplan_event_id,
                        order_id=order['id'],
                        user_id=order['user_id'],
                        order_reference=order['reference'],
                        token=ticket['token'],
                        yurplan_ticket_id=ticket['id'],
                        ticket=valet_ticket
                    ).save()
                except Entry.DoesNotExist:
                    pass

    def __str__(self):
        return self.name


class Entry(models.Model):
    class Meta:
        verbose_name = _('Tarif')

    name = models.CharField(max_length=255)
    price_ht = models.DecimalField(verbose_name=_('Prix HT'), decimal_places=2, max_digits=11)
    price_ttc = models.DecimalField(verbose_name=_('Prix TTC'), decimal_places=2, max_digits=11)
    event = models.ForeignKey(Event, verbose_name=_('Evènement'), related_name='entries')
    yurplan_id = models.IntegerField(blank=True, null=True)
    max_seats = models.IntegerField(default=1600, verbose_name=_('Nombre maximal de place'))
    selling_mode = models.CharField(max_length=20, choices=(
        ('va_only', 'Que pour des membre VA'),
        ('no_va', 'Ne doit pas être VA'),
        ('whatever', 'Qu\'importe')
    ), default='whatever')

    def full_name(self):
        return '{} - {}€'.format(self.name, self.price_ttc)

    def __str__(self):
        return self.name


class SellLocation(models.Model):
    class Meta:
        verbose_name = _('Lieu de vente')
        verbose_name_plural = _('Lieux de vente')

    name = models.CharField(max_length=255)
    latitude = models.DecimalField(decimal_places=10, max_digits=13)
    longitude = models.DecimalField(decimal_places=10, max_digits=13)
    events = models.ManyToManyField(Event, related_name='locations')

    def __str__(self):
        return self.name


class Ticket(models.Model):
    class Meta:
        verbose_name = _('Billet')

    available_ticket_types = (
        ('classic', _('Classique')),
        ('yurplan', 'Yurplan'),
        ('va', 'Carte VA')
    )

    payment_methods = (
        ('CB', _('Carte Bancaire')),
        ('ESP', _('Espèces')),
        ('CHQ', _('Chèque')),
        ('VIR', _('Virement Bancaire')),
    )

    entry = models.ForeignKey(Entry, verbose_name=_('Tarif'), related_name='tickets')
    email = models.EmailField()
    payment_method = models.CharField(max_length=3, choices=payment_methods, verbose_name=_('Méthode de paiement'),
                                      default='CB')
    location = models.ForeignKey(SellLocation, related_name='sells', blank=True, null=True)
    canceled = models.BooleanField(default=False)
    ticket_type = models.CharField(max_length=50, choices=available_ticket_types)
    first_name = models.CharField(max_length=255, verbose_name=_('Prénom'))
    last_name = models.CharField(max_length=255, verbose_name=_('Nom'))
    created_at = models.DateTimeField(auto_now_add=True)

    def full_id(self):
        if self.location:
            return "{}E{}L{}T".format(self.entry.event.pk, self.location.pk, self.pk)
        else:
            if self.yurplan.last():
                return "{}E{}YP{}T".format(self.entry.event.pk, self.yurplan.last().yurplan_ticket_id, self.pk)
            else:
                return "{}EON{}T".format(self.entry.event.pk, self.pk)

    def code(self):
        return security.encrypt({
            'ticket': {'id': self.id},
            'time': str(datetime.now())
        })

    def used(self):
        return self.validation_entry.count() > 0

    def check_entry(self):
        if not self.used():
            Validation(ticket=self).save()
            if self.ticket_type == 'yurplan':
                yurplan.ApiClient().check_ticket(self.entry.event.yurplan_event_id, self.yurplan.last().token)

    def uncheck_entry(self):
        if self.used():
            Validation.objects.filter(ticket=self).delete()
            if self.ticket_type == 'yurplan':
                yurplan.ApiClient().uncheck_ticket(self.entry.event.yurplan_event_id, self.yurplan.last().token)

    def security_hash(self):
        return md5(str(settings.SECRET_KEY+self.full_id()).encode()).hexdigest()

    @staticmethod
    def find_for_code(code):
        yp = re.compile(r'^[0-9]+$')
        if yp.fullmatch(code):
            try:
                return YurplanLink.objects.get(token=code).ticket or None
            except YurplanLink.DoesNotExist:
                return None
        va = re.compile(r'^c[0-9]{12}$')
        if va.fullmatch(code):
            membership = MarsuAPI().get_va(code)
            if 'id' not in membership:
                return None
            try:
                return VALink.objects.get(va_id=membership['id']).ticket or None
            except VALink.DoesNotExist:
                return None
        ss = re.compile(r'^s-[A-Za-z0-9]*-[0-9]*$')
        if ss.fullmatch(code):
            data = str(code).split('-', 3)
            try:
                ticket = Ticket.objects.get(pk=data[2])
                if ticket is None:
                    return None
                if data[1] != ticket.security_hash():
                    return None
                return ticket or None
            except Ticket.DoesNotExist:
                return None

        code = security.decrypt(code)

        try:
            return Ticket.objects.get(pk=code['ticket']['id']) or None
        except Ticket.DoesNotExist:
            return None

    def __str__(self):
        return "Ticket #{}".format(self.full_id())


class VALink(models.Model):
    class Meta:
        verbose_name = _('Carte VA')

    ticket = models.ForeignKey(Ticket, related_name='va', limit_choices_to={'ticket_type': 'va'})
    va_id = models.IntegerField(verbose_name=_('Numéro d\'adhérant'))
    card_id = models.CharField(max_length=15)

    def __str__(self):
        return "VA #{}".format(self.va_id)


class YurplanLink(models.Model):
    class Meta:
        verbose_name = _('Lien Yurplan')

    event_id = models.IntegerField(verbose_name=_('Evènement Yurplan'))
    order_id = models.IntegerField(verbose_name=_('Numéro de commande Yurplan'))
    user_id = models.IntegerField(verbose_name=_('Utilisateur Yurplan'))
    order_reference = models.CharField(max_length=15, verbose_name=_('Référence de commande Yurplan'))
    token = models.CharField(max_length=100, verbose_name=_('Clef du billet'), help_text=_('Ce code est celui '
                                                                                           'constituant le code bare du'
                                                                                           ' billet YurPlan'))
    yurplan_ticket_id = models.IntegerField(verbose_name=_('Identifiant du billet'))
    ticket = models.ForeignKey(Ticket, related_name='yurplan', limit_choices_to={'ticket_type': 'yurplan'})

    def __str__(self):
        return "{} - {}".format(self.order_reference, self.yurplan_ticket_id)


class Validation(models.Model):
    class Meta:
        verbose_name = _('Validation')

    created_at = models.DateTimeField(auto_now_add=True)
    ticket = models.ForeignKey(Ticket, related_name='validation_entry')

    def __str__(self):
        return "Validation #{}".format(self.ticket.full_id())
