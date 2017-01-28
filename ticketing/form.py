from django.forms import ModelForm, CharField

from ticketing.models import Ticket


class TicketForm(ModelForm):

    class Meta:
        fields = ('va_id', 'first_name', 'last_name', 'email', 'payment_method')

    model = Ticket
    va_id = CharField(max_length=15)
