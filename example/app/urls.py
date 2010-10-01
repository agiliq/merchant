
from django.conf.urls.defaults import *

urlpatterns = patterns('app.views',
    url(r'^$', 'index', name='app_index'),
    url(r'^authorize/$', 'authorize', name='app_authorize'),
    url(r'^paypal/$', 'paypal', name='app_paypal'),
    url(r'^eway/$', 'eway', name='app_eway'),
)

# offsite payments
urlpatterns += patterns('app.views',
    url(r'offsite/paypal/$', 'offsite_paypal', name='app_offsite_paypal'),
    url(r'offsite/google-checkout/$', 'offsite_google_checkout', name='app_offsite_google_checkout'),
)