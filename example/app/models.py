from django.db import models
from billing.signals import amazon_fps_payment_signal
import urlparse

def amazon_fps_callback(sender, **kwargs):
    request = kwargs["request"]
    fps = kwargs["integration"]
    request_url = request.build_absolute_uri()
    parsed_url = urlparse.urlparse(request_url)
    query = parsed_url.query
    dd = dict(map(lambda x: x.split("="), query.split("&")))
    fps.purchase(100, dd)
amazon_fps_payment_signal.connect(amazon_fps_callback)
