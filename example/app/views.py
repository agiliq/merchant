
from django.shortcuts import render_to_response
from django.template import RequestContext

def render(request, template, template_vars={}):
    return render_to_response(template, template_vars, RequestContext(request))

def index(request):
    return render(request, 'app/index.html')
