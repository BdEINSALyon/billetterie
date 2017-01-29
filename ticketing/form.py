from django.forms import ModelForm, CharField, ChoiceField, CheckboxInput, ModelChoiceField, RadioSelect
from django.forms.utils import ErrorList
from django.utils.translation import ugettext_lazy as _
from ticketing.models import Ticket, Event


class TicketForm(ModelForm):

    class Meta:
        model = Ticket
        fields = ('va_id', 'first_name', 'last_name', 'email', 'payment_method')

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, instance=None, use_required_attribute=None):
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, instance,
                         use_required_attribute)

    entry = ChoiceField(label=_('Tarif'), required=True, widget=RadioSelect)
    va_id = CharField(max_length=15, label=_('Carte VA'), required=False)

    def set_event(self, event):
        self.fields['entry'].choices = [(entry.pk, entry.full_name()) for entry in event.entries.all()]
        self.fields['entry'].initial = event.entries.first().pk
