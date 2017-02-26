# tables.py
from django.utils import timezone
from table import Table
from table.columns import Column
from table.utils import Accessor

from ticketing.models import Ticket


# noinspection PyMethodMayBeStatic
class StatusColumn(Column):

    def render(self, obj):
        if obj.used():
            return timezone.localtime(obj.validation_entry.last().created_at).strftime("%Y-%m-%d %H:%M:%S")
        else:
            return 'Non'


# noinspection PyMethodMayBeStatic
class CodeColumn(Column):

    def render(self, obj):
        return '<a href="#" data-code="s-{}-{}" class="code-input btn btn-primary">Valider</a>'.format(obj.security_hash(), obj.id)


class TicketsTable(Table):
    id = Column(field='id', header='#')
    first_name = Column(field='first_name', header='Prénom')
    last_name = Column(field='last_name', header='Nom')
    used = StatusColumn(searchable=False, sortable=False, header='Entrée')
    code = CodeColumn(searchable=False, sortable=False, field='code', header='')

    class Meta:
        model = Ticket
        ajax = True


