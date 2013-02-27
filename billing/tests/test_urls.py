from django.conf.urls import *
from billing import get_integration

pay_pal = get_integration("pay_pal")
fps = get_integration("amazon_fps")
braintree = get_integration("braintree_payments")

urlpatterns = patterns('',
      ('^paypal-ipn-url/', include(pay_pal.urls)),
      ('^fps/', include(fps.urls)),
      ('^braintree/', include(braintree.urls)),
)
