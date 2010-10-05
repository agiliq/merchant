from django.conf.urls.defaults import *

urlpatterns = patterns('billing.views',
    url(r'^notify-handler$', 'notify_handler', name='billing_notify_handler'),
)