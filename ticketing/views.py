import json
from datetime import datetime, timedelta

from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.db.models import Count
from django.http.response import JsonResponse, HttpResponseNotFound, HttpResponseNotAllowed, HttpResponseRedirect, \
    HttpResponseForbidden
from django.template import Template
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView

from ticketing import security
from ticketing import yurplan
from ticketing.form import TicketForm, CheckForm
from ticketing.marsu import MarsuAPI
from ticketing.models import Ticket, Entry, VALink, Event, YurplanLink, SellLocation


class SellTicket(TemplateView):
    form = TicketForm
    template_name = 'ticketing/sell_ticket.html'
    http_method_names = ('get', 'post')

    def get_context_data(self, **kwargs):
        event = Event.objects.get(pk=self.kwargs['event'])
        location = SellLocation.objects.get(pk=self.kwargs['location'])
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
        event = Event.objects.get(pk=self.kwargs['event'])
        if request.user.is_anonymous() or not event.can_be_managed_by(request.user):
            return HttpResponseRedirect('/')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, event, location, **params):
        event = Event.objects.get(pk=event)
        location = SellLocation.objects.get(pk=location)

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

        msg = EmailMultiAlternatives("Votre billet pour le {}".format(event.name),
                                     "Ce billet est distribué qu'au format HTML",
                                     "BdE INSA Lyon <billetterie@mg.bde-insa-lyon.fr>", [ticket.email])
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
    event = Event.objects.get(pk=event)
    if request.user.is_anonymous() or not event.can_be_managed_by(request.user):
        return HttpResponseRedirect('/')
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


def valethon(request, event):
    if request.method == 'GET':
        event = Event.objects.get(id=event)
        if request.user.is_anonymous() or not event.can_be_managed_by(request.user):
            return HttpResponseRedirect('/')
        sold_tickets = Ticket.objects.filter(entry__event=event, canceled=False).count()
        sales_opening_period = (event.sales_closing - event.sales_opening).days
        days_of_sales = sales_opening_period - event.closed_days_count or 1
        stats = {'sold_tickets': sold_tickets, 'left_tickets': event.max_seats - sold_tickets,
                 'fill': sold_tickets / event.max_seats * 100,
                 'left_tickets_by_days': (event.max_seats - sold_tickets) /
                                         (
                                             days_of_sales
                                         ),
                 'sales': []}
        for entry in event.entries.all():
            stats['sales'].append({
                'name': entry.name,
                'sold_tickets': entry.tickets.count()
            })
        stats['by_day'] = []
        locations = event.locations.all()
        for i in range(0, sales_opening_period + 1):
            sales_of_day = Ticket.objects.filter(entry__event=event, canceled=False,
                                                 created_at__gte=event.sales_opening.date() + timedelta(days=i),
                                                 created_at__lte=event.sales_opening.date() + timedelta(days=i + 1)
                                                 ).count()
            sales_at_this_day = Ticket.objects.filter(entry__event=event, canceled=False,
                                                      created_at__gte=event.sales_opening.date(),
                                                      created_at__lte=event.sales_opening.date() + timedelta(days=i + 1)
                                                      ).count()
            sales_of_day = {
                'day': event.sales_opening.date() + timedelta(days=i),
                'sales': sales_of_day,
                'at_this_day': sales_at_this_day,
                'by_location': []
            }
            for location in locations:
                sales_of_day['by_location'].append({
                    'sales': Ticket.objects.filter(entry__event=event, canceled=False,
                                                   created_at__gte=event.sales_opening.date() + timedelta(days=i),
                                                   created_at__lte=event.sales_opening.date() + timedelta(days=i + 1),
                                                   location=location
                                                   ).count()
                })
            sales_of_day['by_location'].append({
                'sales': Ticket.objects.filter(entry__event=event, canceled=False,
                                               created_at__gte=event.sales_opening.date() + timedelta(days=i),
                                               created_at__lte=event.sales_opening.date() + timedelta(days=i + 1),
                                               location=None
                                               ).count()
            })
            stats['by_day'].append(sales_of_day)
        return TemplateResponse(request, 'ticketing/participants/valethon.html', context={
            'stats': stats,
            'now': datetime.now,
            'event': event,
            'locations': locations
        })
    else:
        return HttpResponseNotAllowed(permitted_methods=('GET',))


def check_participant(request, event):
    event = Event.objects.get(pk=event)
    if request.user.is_anonymous() or not event.can_be_managed_by(request.user):
        return HttpResponseRedirect('/')
    if request.method == 'GET':
        return TemplateResponse(request, template='ticketing/check/check.html', context={
            'form': CheckForm(),
            'tickets': Ticket.objects.filter(entry__event=event, canceled=False),
            'event': event
        })
    if request.method == 'POST':
        code = request.POST['ticket_barre_code']
        ticket = Ticket.find_for_code(code)
        if ticket is None:
            return TemplateResponse(request, template='ticketing/check/ko.html', context={
                'reason': 'Aucun billet pour cette personne dans la base.',
                'event': event
            })
        if ticket.used():
            return TemplateResponse(request, template='ticketing/check/ko.html', context={
                'reason': 'Le billet a été utilisé le {} (GMT).'.format(ticket.validation_entry.last().created_at),
                'event': event
            })
        ticket.check_entry()
        return TemplateResponse(request, template='ticketing/check/ok.html', context={
            'event': event
        })


def ticket_va_swap(request, event, ticket):
    event = Event.objects.get(pk=event)
    if request.user.is_anonymous() or not event.can_be_managed_by(request.user) or not request.user.is_staff:
        return HttpResponseRedirect('/')
    ticket = Ticket.objects.get(pk=ticket, entry__event=event)
    ticket_form = TicketForm()
    if request.method == 'GET':
        return TemplateResponse(request, template='ticketing/participants/ticket_va_swap.html', context={
            'form': ticket_form,
            'ticket': ticket,
            'event': event
        })
    if request.method == 'POST':
        membership = MarsuAPI().get_va(request.POST['va_id'])
        if 'id' not in membership:
            return JsonResponse({
                'success': False,
                'reason': 'La carte VA n\'existe pas ou n\'a pas été activé',
                'type': 'va'
            }, content_type='application/json')
        if VALink.objects.filter(va_id=membership['id']).count() > 0:
            return JsonResponse({
                'success': False,
                'reason': 'La carte VA a déjà été utilisé pour une autre place !',
                'type': 'va'
            }, content_type='application/json')
        ticket.va.last().delete()
        va_link = VALink(ticket=ticket, card_id=request.POST['va_id'],
                         va_id=membership['id'])
        va_link.save()
        ticket.first_name = request.POST['first_name']
        ticket.last_name = request.POST['last_name']
        ticket.email = request.POST['email']
        ticket.save()
        return JsonResponse({
            'success': True,
            'ticket': '#{}'.format(ticket.full_id()),
            'type': ticket.ticket_type
        }, content_type='application/json')
