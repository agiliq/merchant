
from django.conf.urls.defaults import *

urlpatterns = patterns('app.views',
    url(r'^$', 'index', name='app_index'),
    url(r'^authorize/$', 'authorize', name='app_authorize'),
    url(r'^paypal/$', 'paypal', name='app_paypal'),
    url(r'^eway/$', 'eway', name='app_eway'),
)
