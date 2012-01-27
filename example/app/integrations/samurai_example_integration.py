from billing.integrations.samurai_integration import SamuraiIntegration
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
try:
    import json
except ImportError:
    import simplejson as json
except ImportError:
    from django.utils import simplejson as json

class SamuraiExampleIntegration(SamuraiIntegration):
    @csrf_exempt
    def transaction(self, request):
        resp = self.gateway.purchase(1, request.POST["payment_method_token"])
        return HttpResponse(resp["response"].to_json())
