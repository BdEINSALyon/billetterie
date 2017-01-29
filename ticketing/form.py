from django.forms import ModelForm, CharField
from django.utils.translation import ugettext_lazy as _
from ticketing.models import Ticket


class TicketForm(ModelForm):

    class Meta:
        model = Ticket
        fields = ('va_id', 'first_name', 'last_name', 'email', 'payment_method')

    va_id = CharField(max_length=15, label=_('Carte VA'), required=False)
