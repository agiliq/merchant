
from django.conf.urls.defaults import *
from billing import get_integration
from app.views import google_checkout_obj, pay_pal_obj, amazon_fps_obj

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
    url(r'offsite/world_pay/$', 'offsite_world_pay', name='app_offsite_world_pay'),
    url(r'offsite/amazon_fps/$', 'offsite_amazon_fps', name='app_offsite_amazon_fps'),
)

# paypal payment notification handler
urlpatterns += patterns('',
    (r'^paypal-ipn-handler/', include(pay_pal_obj.urls)),
)
urlpatterns += patterns('',
    (r'^', include(google_checkout_obj.urls)),
)

urlpatterns += patterns('',
    (r'^fps/', include(amazon_fps_obj.urls)),
)

urlpatterns += patterns('django.views.generic.simple',
    url(r'offsite/paypal/done/$', 
        'direct_to_template', 
        {'template': 'app/payment_done.html'},
        name='app_offsite_paypal_done'),
    url(r'offsite/google-checkout/done/$', 
        'direct_to_template', 
        {'template': 'app/payment_done.html'},
        name='app_offsite_google_checkout_done'),
)
