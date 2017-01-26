from django.shortcuts import render
from django.views import generic as views
from django.views.generic import ListView

from ticketing import models

# Create your views here.


class EventsList(ListView):
    model = models.Event
    template_name = 'ticketing/events.html'
