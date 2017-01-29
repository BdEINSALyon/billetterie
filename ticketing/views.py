from django.http.response import JsonResponse, HttpResponseNotFound, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView

from ticketing import models
from ticketing.form import TicketForm
from ticketing.marsu import MarsuAPI


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
