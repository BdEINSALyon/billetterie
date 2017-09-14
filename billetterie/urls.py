from django.conf.urls import url

from billetterie.views import welcome

urlpatterns = [
    url(r'^$', welcome, name='welcome')
]
