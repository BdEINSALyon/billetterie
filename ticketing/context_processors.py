from ticketing.models import Event


def events(request):
    return {
        'events': Event.objects.all
    }
