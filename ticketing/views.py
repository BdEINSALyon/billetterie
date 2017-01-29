from django.shortcuts import render
from django.views import generic as views
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import TemplateView

from ticketing import models

# Create your views here.
from ticketing.form import TicketForm
from ticketing.models import Ticket


class EventsList(ListView):
    model = models.Event
    template_name = 'ticketing/events.html'


class EventView(DetailView):
    model = models.Event
    template_name = 'ticketing/event.html'


class SellTicket(TemplateView):
    form = TicketForm
    template_name = 'ticketing/sell_ticket.html'

    def get_context_data(self, **kwargs):
        data = {'event': models.Event.objects.get(pk=self.kwargs['event']),
                'location': models.SellLocation.objects.get(pk=self.kwargs['location']),
                'form': self.get_form()}
        kwargs.update(data)
        return kwargs

    def get_form(self):
        return self.form()
