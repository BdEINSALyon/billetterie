from django.conf.urls import url

from ticketing import pdf
from ticketing.views import SellTicket, check_va, list_participants, welcome

urlpatterns = [
    url(r'^events/(?P<event>[0-9]+)/participants$', list_participants, name='list_participants'),
    url(r'^events/(?P<event>[0-9]+)/selling/(?P<location>[0-9]+)', SellTicket.as_view(), name='event_sale'),
    url(r'^print/(?P<code>[A-Za-z0-9=+]+)', pdf.generate_ticket, name='pdf_ticket'),
    url(r'^va/check', check_va, name='check_va'),
    url(r'^$', welcome, name='welcome')
]
