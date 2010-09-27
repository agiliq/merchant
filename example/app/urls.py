
from django.conf.urls.defaults import *

urlpatterns = patterns('app.views',
    url(r'^$', 'index', name='app_index'),
)
