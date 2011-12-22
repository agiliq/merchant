
from django.conf.urls.defaults import *
from billing import get_integration

google_checkout_obj = get_integration("google_checkout")
pay_pal_obj = get_integration("pay_pal")
amazon_fps_obj = get_integration("fps")
fps_recur_obj = get_integration("fps")
world_pay_obj = get_integration("world_pay")
braintree_obj = get_integration("braintree_payments")

urlpatterns = patterns('app.views',
    url(r'^$', 'index', name='app_index'),
    url(r'^authorize/$', 'authorize', name='app_authorize'),
    url(r'^paypal/$', 'paypal', name='app_paypal'),
    url(r'^eway/$', 'eway', name='app_eway'),
    url(r'^braintree/$', 'braintree', name='app_braintree'),
    url(r'^stripe/$', 'stripe', name='app_stripe'),
)

# offsite payments
urlpatterns += patterns('app.views',
    url(r'offsite/paypal/$', 'offsite_paypal', name='app_offsite_paypal'),
    url(r'offsite/google-checkout/$', 'offsite_google_checkout', name='app_offsite_google_checkout'),
    url(r'offsite/world_pay/$', 'offsite_world_pay', name='app_offsite_world_pay'),
    url(r'offsite/amazon_fps/$', 'offsite_amazon_fps', name='app_offsite_amazon_fps'),
    url(r'offsite/braintree/$', 'offsite_braintree', name='app_offsite_braintree'),
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

urlpatterns += patterns('',
    (r'^braintree/', include(braintree_obj.urls)),
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
