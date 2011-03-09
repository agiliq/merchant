from django.conf.urls.defaults import *
from billing import get_integration

pay_pal = get_integration("pay_pal")

urlpatterns = patterns('',
      ('^paypal-ipn-url/', include(pay_pal.urls)),
)
