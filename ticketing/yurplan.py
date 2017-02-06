import json

import requests
from django.conf import settings


class ApiClient:
    _AUTH_TOKEN = ""

    @staticmethod
    def _authenticate():
        auth_request = requests.post('https://api.yurplan.com/v1/token', data={
            'grant_type': 'client_credentials',
            'scope': 'pro',
            'client_id': settings.YURPLAN_APP_ID,
            'client_secret': settings.YURPLAN_APP_SECRET,
        })
        auth = json.loads(auth_request.text)
        if auth['status'] == 200:
            ApiClient._AUTH_TOKEN = auth['results']['access_token']
            return True
        else:
            return False

    def get_order(self, event_id, order_id, try_auth=True):
        r = requests.get('https://api.yurplan.com/v1/events/{}/orders/{}'.format(event_id, order_id),
                         headers={
                             'Authorization': 'Bearer {}'.format(ApiClient._AUTH_TOKEN)
                         })
        if r.status_code == 200:
            return json.loads(r.text)['results']
        else:
            if try_auth and r.status_code != 404:
                ApiClient._authenticate()
                return self.get_order(event_id, order_id, try_auth=False)
            else:
                return None

    def get_ticket(self, event_id, ticket_id, try_auth=True):
        r = requests.get('https://api.yurplan.com/v1/events/{}/tickets/{}'.format(event_id, ticket_id),
                         headers={
                             'Authorization': 'Bearer {}'.format(ApiClient._AUTH_TOKEN)
                         })
        if r.status_code == 200:
            return json.loads(r.text)['results']
        else:
            if try_auth and r.status_code != 404:
                ApiClient._authenticate()
                return self.get_order(event_id, ticket_id, try_auth=False)
            else:
                return None

    def check_ticket(self, event_id, ticket_id, try_auth=True):
        r = requests.put('https://api.yurplan.com/v1/events/{}/tickets/{}/check?by_token=true'
                         .format(event_id, ticket_id),
                         headers={
                             'Authorization': 'Bearer {}'.format(ApiClient._AUTH_TOKEN)
                         })
        if r.status_code == 200:
            return json.loads(r.text)['results']
        else:
            if try_auth and r.status_code != 404:
                ApiClient._authenticate()
                return self.check_ticket(event_id, ticket_id, try_auth=False)
            else:
                return None

    def uncheck_ticket(self, event_id, ticket_id, try_auth=True):
        r = requests.put('https://api.yurplan.com/v1/events/{}/tickets/{}/uncheck?by_token=true'
                         .format(event_id, ticket_id),
                         headers={
                             'Authorization': 'Bearer {}'.format(ApiClient._AUTH_TOKEN)
                         })
        if r.status_code == 200:
            return json.loads(r.text)['results']
        else:
            if try_auth and r.status_code != 404:
                ApiClient._authenticate()
                return self.uncheck_ticket(event_id, ticket_id, try_auth=False)
            else:
                return None

