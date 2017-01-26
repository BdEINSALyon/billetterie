from django.conf.urls import url

from ticketing.views import EventsList, EventView

urlpatterns = [
    url(r'^$', EventsList.as_view(), name='events'),
    url(r'^(?P<pk>[0-9]*)', EventView.as_view(), name='event'),
    url(r'^(?P<event>[0-9]*)/selling/(?P<location>[0-9]*)', EventsList.as_view(), name='event_sale'),
    url(r'^(?P<event>[0-9]*)/ticket/(?P<pk>[0-9]*)', EventsList.as_view(), name='ticket')
]
