import requests
from django.conf import settings


class MarsuAPI:
    app_id = settings.MARSU_APP_ID
    app_secret = settings.MARSU_APP_SECRET
    token = None

    def refresh_token(self):
        if self.token is None:
            token_request = requests.get('https://adhesion.bde-insa-lyon.fr/api/auth',
                                         {'app_id': self.app_id, 'app_secret': self.app_secret})
            self.token = token_request.json()['token']

    def get_va(self, card_id):
        self.refresh_token()
        return requests.get('https://adhesion.bde-insa-lyon.fr/api/membership', {
            'code': card_id
        }, headers={
            'Authorization': 'Bearer {}'.format(self.token)
        }).json()
