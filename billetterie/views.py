from django.shortcuts import render

# Create your views here.
from django.template.response import TemplateResponse


def welcome(request):
    return TemplateResponse(request, 'billetterie/welcome.html')
