from django.conf.urls import *
from billing import get_integration
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

google_checkout_obj = get_integration("google_checkout")
authorize_net_obj = get_integration("authorize_net_dpm")
pay_pal_obj = get_integration("pay_pal")
amazon_fps_obj = get_integration("fps")
fps_recur_obj = get_integration("fps")
world_pay_obj = get_integration("world_pay")
braintree_obj = get_integration("braintree_payments")
stripe_obj = get_integration("stripe_example")
ogone_obj = get_integration("ogone_payments")

urlpatterns = patterns('app.views',
    url(r'^$', 'index', name='app_index'),
    url(r'^authorize/$', 'authorize', name='app_authorize'),
    url(r'^paypal/$', 'paypal', name='app_paypal'),
    url(r'^eway/$', 'eway', name='app_eway'),
    url(r'^braintree/$', 'braintree', name='app_braintree'),
    url(r'^stripe/$', 'stripe', name='app_stripe'),
    url(r'^paylane/$', 'paylane', name='app_paylane'),
    url(r'^beanstream/$', 'beanstream', name='app_beanstream'),
    url(r'^chargebee/$', 'chargebee', name='app_chargebee'),
    url(r'^bitcoin/$', 'bitcoin', name='app_bitcoin'),
    url(r'^bitcoin/done/$', 'bitcoin_done', name='app_bitcoin_done'),
)

# offsite payments
urlpatterns += patterns('app.views',
    url(r'offsite/authorize_net/$', 'offsite_authorize_net', name='app_offsite_authorize_net'),
    url(r'offsite/paypal/$', 'offsite_paypal', name='app_offsite_paypal'),
    url(r'offsite/google-checkout/$', 'offsite_google_checkout', name='app_offsite_google_checkout'),
    url(r'offsite/world_pay/$', 'offsite_world_pay', name='app_offsite_world_pay'),
    url(r'offsite/amazon_fps/$', 'offsite_amazon_fps', name='app_offsite_amazon_fps'),
    url(r'offsite/braintree/$', 'offsite_braintree', name='app_offsite_braintree'),
    url(r'offsite/stripe/$', 'offsite_stripe', name='app_offsite_stripe'),
    url(r'offsite/eway/$', 'offsite_eway', name='app_offsite_eway'),

    # redirect handler
    url(r'offsite/eway/done/$', 'offsite_eway_done'),
    url(r'offsite/ogone/$', 'offsite_ogone', name='app_offsite_ogone'),
)

urlpatterns += patterns('',
    (r'^authorize_net-handler/', include(authorize_net_obj.urls)),
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

urlpatterns += patterns('',
    (r'^stripe/', include(stripe_obj.urls)),
)

urlpatterns += patterns('',
    url(r'offsite/paypal/done/$',
        csrf_exempt(TemplateView.as_view(template_name="app/payment_done.html")),
        name='app_offsite_paypal_done'),
    url(r'offsite/google-checkout/done/$',
        TemplateView.as_view(template_name="app/payment_done.html"),
        name='app_offsite_google_checkout_done'),
)

urlpatterns += patterns('app.views',
    url(r'^we_pay/$', 'we_pay', name="app_we_pay"),
    url(r'we_pay_redirect/$', 'we_pay_redirect', name="app_we_pay_redirect"),
    url(r'^we_pay_ipn/$', 'we_pay_ipn', name="app_we_pay_ipn"),
)

urlpatterns += patterns('',
    (r'^ogone/', include(ogone_obj.urls)),
)
