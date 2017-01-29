from django.http.response import JsonResponse, HttpResponseNotFound, HttpResponseNotAllowed, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView

from ticketing import models
from ticketing.form import TicketForm
from ticketing.marsu import MarsuAPI
from ticketing.models import Ticket, Entry, VALink


class EventsList(ListView):
    model = models.Event
    template_name = 'ticketing/events.html'


class EventView(DetailView):
    model = models.Event
    template_name = 'ticketing/event.html'


class SellTicket(TemplateView):
    form = TicketForm
    template_name = 'ticketing/sell_ticket.html'
    http_method_names = ('get', 'post')

    def get_context_data(self, **kwargs):
        event = models.Event.objects.get(pk=self.kwargs['event'])
        location = models.SellLocation.objects.get(pk=self.kwargs['location'])
        data = {'event': event,
                'location': location,
                'form': self.get_form(event)}
        kwargs.update(data)
        return kwargs

    def get_form(self, event):
        form = self.form()
        form.set_event(event)
        return form

    def post(self, request, event, location, **params):
        event = models.Event.objects.get(pk=event)
        location = models.SellLocation.objects.get(pk=location)

        ticket = Ticket()
        ticket.entry = Entry.objects.get(id=request.POST['entry'])
        ticket.first_name = request.POST['first_name']
        ticket.last_name = request.POST['last_name']
        ticket.payment_method = request.POST['payment_method']
        ticket.email = request.POST['email']
        ticket.location = location
        ticket.ticket_type = 'classic'

        if ticket.save() is not None:
            return TemplateResponse(request, 'ticketing/failed.html')

        if request.POST['va_id'] != '':
            membership = MarsuAPI().get_va(request.POST['va_id'])
            if VALink.objects.filter(va_id=membership['id']).count() > 0:
                ticket.delete()
                return TemplateResponse(request, 'ticketing/already_used_va.html')

            va_link = VALink(ticket=ticket, card_id=request.POST['va_id'],
                             va_id=membership['id'])
            va_link.save()

            ticket.ticket_type = 'va'
            ticket.save()
        else:
            # TODO: Send the ticket by email
            pass

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def check_va(request):
    if request.method == 'POST':
        api = MarsuAPI().get_va(request.POST['code'])
        if 'code' in api:
            return HttpResponseNotFound(content_type='application/json')
        else:
            student = {key: api[key] for key in ['id', 'first_name', 'last_name', 'email']}
            return JsonResponse(student, content_type='application/json')
    else:
        return HttpResponseNotAllowed(permitted_methods=('POST',))
