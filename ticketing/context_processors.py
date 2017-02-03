from ticketing.models import Event


def events(request):
    allowed_events = []
    if not request.user.is_anonymous():
        for event in Event.objects.all():
            if event.can_be_managed_by(request.user):
                allowed_events.append(event)
        return {
            'allowed_events': allowed_events
        }
    else:
        return {
            'allowed_events': []
        }
