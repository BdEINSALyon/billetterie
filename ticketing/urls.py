from django.conf.urls import url

from ticketing.views import EventsList, EventView, SellTicket, check_va

urlpatterns = [
    url(r'^events$', EventsList.as_view(), name='events'),
    url(r'^events/(?P<pk>[0-9]*)$', EventView.as_view(), name='event'),
    url(r'^events/(?P<event>[0-9]*)/selling/(?P<location>[0-9]*)', SellTicket.as_view(), name='event_sale'),
    url(r'^events/(?P<event>[0-9]*)/ticket/(?P<pk>[0-9]*)', EventsList.as_view(), name='ticket'),
    url(r'^va/check', check_va, name='check_va')
]
