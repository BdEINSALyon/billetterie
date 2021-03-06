"""accounts URL configuration
"""
from django.conf.urls import url

from account import views

urlpatterns = [
    url(r'^oauth/(?P<provider>[a-z_]*)/callback', views.OAuthCallback.as_view(), name='oauth_callback'),
    url(r'^oauth/(?P<provider>[a-z_]*)/login', views.OAuthLogin.as_view(),  name='oauth_login'),
]
