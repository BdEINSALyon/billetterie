import json
from datetime import datetime

from django.core.mail import EmailMultiAlternatives
from django.http.response import JsonResponse, HttpResponseNotFound, HttpResponseNotAllowed, HttpResponseRedirect, \
    HttpResponseForbidden
from django.template import Template
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView

from ticketing import models
from ticketing import security
from ticketing import yurplan
from ticketing.form import TicketForm
from ticketing.marsu import MarsuAPI
from ticketing.models import Ticket, Entry, VALink, Event, YurplanLink


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

    def dispatch(self, request, *args, **kwargs):
        event = models.Event.objects.get(pk=self.kwargs['event'])
        if request.user.is_anonymous() or not event.can_be_managed_by(request.user):
            return HttpResponseRedirect('/')
        return super().dispatch(request, *args, **kwargs)

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
            return JsonResponse({
                'success': False,
                'reason': 'Le formulaire est mal remplis et ne permet pas de créer la place',
                'type': 'va'
            }, content_type='application/json')

        if request.POST['va_id'] != '':
            membership = MarsuAPI().get_va(request.POST['va_id'])
            if 'id' not in membership:
                ticket.delete()
                return JsonResponse({
                    'success': False,
                    'reason': 'La carte VA n\'existe pas ou n\'a pas été activé',
                    'type': 'va'
                }, content_type='application/json')
            if VALink.objects.filter(va_id=membership['id']).count() > 0:
                ticket.delete()
                return JsonResponse({
                    'success': False,
                    'reason': 'La carte VA a déjà été utilisé pour une autre place !',
                    'type': 'va'
                }, content_type='application/json')

            va_link = VALink(ticket=ticket, card_id=request.POST['va_id'],
                             va_id=membership['id'])
            va_link.save()

            ticket.ticket_type = 'va'
            ticket.save()

        msg = EmailMultiAlternatives("Votre billet pour {}".format(event.name),
                                     "Ce billet est distribué qu'au format HTML",
                                     "billetterie@mg.bde-insa-lyon.fr", [ticket.email])
        message = TemplateResponse(request,
                                   template='ticketing/email.html',
                                   context={
                                       'event': event,
                                       'ticket': ticket,
                                       'code': security.encrypt({
                                           'ticket': {
                                               'id': ticket.id
                                           },
                                           'time': str(datetime.now())
                                       })
                                   }).render()
        msg.attach_alternative(message, "text/html")

        msg.send()

        return JsonResponse({
            'success': True,
            'ticket': '#{}'.format(ticket.full_id()),
            'type': ticket.ticket_type
        }, content_type='application/json')


def list_participants(request, event):
    event = models.Event.objects.get(pk=event)
    return TemplateResponse(request, 'ticketing/participants/index.html', context={
        'tickets': Ticket.objects.filter(entry__event=event)
    })


def welcome(request):
    if request.user.is_anonymous():
        return TemplateResponse(request, 'login.html')
    else:
        return TemplateResponse(request, 'ticketing/welcome.html')


def check_va(request):
    if request.method == 'POST':
        api = MarsuAPI().get_va(request.POST['code'])
        if 'code' in api:
            return HttpResponseNotFound(content_type='application/json')
        else:
            student = {key: api[key] for key in ['id', 'first_name', 'last_name', 'email']}
            student['tickets'] = VALink.objects.filter(va_id=student['id']).count()
            return JsonResponse(student, content_type='application/json')
    else:
        return HttpResponseNotAllowed(permitted_methods=('POST',))


@csrf_exempt
def yurplan_webhook(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        if not data['is_test']:
            event = Event.objects.filter(yurplan_event_id=data['event_id']).last()
            if event is not None:
                yurplan_order = data['reference']
                event.load_yurplan_order(yurplan_order)
                return JsonResponse({'success': True, 'data': data}, content_type='application/json')
        return JsonResponse({'success': False, 'data': data}, content_type='application/json')
    else:
        return HttpResponseNotAllowed(permitted_methods=('POST',))



