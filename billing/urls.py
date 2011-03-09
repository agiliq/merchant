from django.conf.urls.defaults import *

urlpatterns = patterns('billing.views',
    url(r'^gc-notify-handler$', 'gc_notify_handler', name='billing_gc_notify_handler'),
)
