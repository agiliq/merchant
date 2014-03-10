import base64
import decimal
import json
import logging

from django.conf import settings
from django.core.signing import TimestampSigner
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
import lxml
import requests

from billing import Integration, get_gateway, IntegrationNotConfigured
from billing.gateways.global_iris_gateway import GlobalIrisBase
from billing.utils.credit_card import Visa, MasterCard, Maestro, CreditCard
from billing.utils.json import chain_custom_encoders, chain_custom_decoders
import billing.utils.credit_card

log = logging.getLogger(__name__)


def get_signer():
    return TimestampSigner(salt="billing.global_iris_real_mpi_integration")


class GlobalIrisRealMpiIntegration(GlobalIrisBase, Integration):
    display_name = "Global Iris RealMPI"

    base_url = "https://remote.globaliris.com/realmpi"

    def get_gateway(self):
        return get_gateway("global_iris")

    def __init__(self, config=None, test_mode=None):
        super(GlobalIrisRealMpiIntegration, self).__init__(config=config, test_mode=test_mode)
        self.gateway = self.get_gateway()

    def card_supported(self, card):
        return card.card_type in [Visa, MasterCard, Maestro]

    def send_3ds_verifyenrolled(self, data):
        return self.handle_3ds_verifyenrolled_response(self.do_request(self.build_3ds_verifyenrolled_xml(data)))

    def handle_3ds_verifyenrolled_response(self, response):
        if response.status_code != 200:
            return GlobalIris3dsError(response.reason, response)
        return GlobalIris3dsVerifyEnrolled(response.content)

    def build_3ds_verifyenrolled_xml(self, data):
        all_data = self.standardize_data(data)
        return render_to_string("billing/global_iris_real_mpi_3ds_verifyenrolled_request.xml", all_data).encode('utf-8')

    def encode_merchant_data(self, data_dict):
        # resourcecentre.globaliris.com talks about encrypting this data.
        # Encryption is not necessary here, since the data has been either
        # entered by the user, or relating to the users stuff, and we are sending
        # it only to services we trust (RealMPI and their bank). However, we do
        # need to ensure that there is no tampering (which encryption does not
        # guarantee), so we sign it.
        return base64.encodestring(get_signer().sign(json.dumps(data_dict,
                                                                default=json_encoder_func,
                                                                )))

    def decode_merchant_data(self, s):
        return json.loads(get_signer().unsign(base64.decodestring(s),
                                              max_age=10*60*60), # Shouldn't take more than 1 hour to fill in auth details!
                          object_hook=json_decoder_func)

    def redirect_to_acs_url(self, enrolled_response, term_url, merchant_data):
        return render_to_response("billing/global_iris_real_mpi_redirect_to_acs.html",
                                  {'enrolled_response': enrolled_response,
                                   'term_url': term_url,
                                   'merchant_data': self.encode_merchant_data(merchant_data),
                                   })

    def parse_3d_secure_request(self, request):
        """
        Extracts the PaRes and merchant data from the HTTP request that is sent
        to the website when the user returns from the 3D secure website.
        """
        return request.POST['PaRes'], self.decode_merchant_data(request.POST['MD'])

    def send_3ds_verifysig(self, pares, data):
        return self.handle_3ds_verifysig_response(self.do_request(self.build_3ds_verifysig_xml(pares, data)))

    def handle_3ds_verifysig_response(self, response):
        if response.status_code != 200:
            return GlobalIris3dsError(response.reason, response)
        return GlobalIris3dsVerifySig(response.content)

    def build_3ds_verifysig_xml(self, pares, data):
        all_data = self.standardize_data(data)
        all_data['pares'] = pares
        return render_to_string("billing/global_iris_real_mpi_3ds_verifysig_request.xml", all_data).encode('utf-8')


def encode_credit_card_as_json(obj):
    if isinstance(obj, CreditCard):
        card_type = getattr(obj, 'card_type', None)
        if card_type is not None:
            card_type = card_type.__name__

        return {'__credit_card__': True,
                'first_name': obj.first_name,
                'last_name': obj.last_name,
                'cardholders_name': obj.cardholders_name,
                'month': obj.month,
                'year': obj.year,
                'number': obj.number,
                'verification_value': obj.verification_value,
                'card_type': card_type,
                }
    raise TypeError("Unknown type %s" % obj.__class__)


def decode_credit_card_from_dict(dct):
    if '__credit_card__' in dct:
        d = dct.copy()
        d.pop('__credit_card__')
        d.pop('card_type')
        retval = CreditCard(**d)
        card_type = dct.get('card_type', None) # put there by Gateway.validate_card
        if card_type is not None:
            # Get the credit card class with this name
            retval.card_type = getattr(billing.utils.credit_card, card_type)
        return retval
    return dct


def encode_decimal_as_json(obj):
    if isinstance(obj, decimal.Decimal):
        return {'__decimal__': True,
                'value': str(obj),
                }
    return TypeError("Unknown type %s" % obj.__class__)


def decode_decimal_from_dict(dct):
    if '__decimal__' in dct:
        return decimal.Decimal(dct['value'])
    return dct


json_encoder_func = chain_custom_encoders([encode_credit_card_as_json, encode_decimal_as_json])
json_decoder_func = chain_custom_decoders([decode_credit_card_from_dict, decode_decimal_from_dict])


class GlobalIris3dsAttempt(object):
    pass


class GlobalIris3dsError(GlobalIris3dsAttempt):
    error = True

    def __init__(self, message, response):
        self.message = message
        self.response = response

    def __repr__(self):
        return "GlobalIris3dsError(%r, %r)" % (self.message, self.response)


class GlobalIris3dsResponse(GlobalIris3dsAttempt):
    error = False


class GlobalIris3dsVerifyEnrolled(GlobalIris3dsResponse):
    def __init__(self, xml_content):
        tree = lxml.etree.fromstring(xml_content)
        self.response_code = tree.find('result').text
        enrolled_node = tree.find('enrolled')
        self.enrolled = enrolled_node is not None and enrolled_node.text == "Y"
        self.message = tree.find('message').text
        if self.response_code in ["00", "110"]:
            self.url = tree.find('url').text
            self.pareq = tree.find('pareq').text
        else:
            self.error = True
            log.warning("3Ds verifyenrolled error", extra={'response_xml': xml_content})


    def proceed_with_auth(self, card):
        """
        Returns a tuple (bool, dict) indicating if you can
        proceed directly with authorisation.

        If the bool == True, you must pass the data in the dict as additional
        data to the gateway.purchase() method.
        """
        if self.error:
            return False, {}
        if not self.enrolled and (self.url is None or self.url == ""):
            eci = 6 if card.card_type is Visa else 1
            return True, {'mpi': {'eci': eci}}
        return False, {}


class GlobalIris3dsVerifySig(GlobalIris3dsResponse):
    def __init__(self, xml_content):
        tree = lxml.etree.fromstring(xml_content)
        self.response_code = tree.find('result').text
        self.message = tree.find('message').text
        if self.response_code == "00":
            threed = tree.find('threedsecure')
            self.status = threed.find('status').text
            if self.status in ["Y", "A"]:
                self.eci = threed.find('eci').text
                self.xid = threed.find('xid').text
                self.cavv = threed.find('cavv').text
        else:
            self.error = True
            log.warning("3Ds verifysig error", extra={'response_xml': xml_content})

    def proceed_with_auth(self, card):
        """
        Returns a tuple (bool, dict) indicating if you can
        proceed with authorisation.

        If the bool == True, you must pass the data in the dict as additional
        data to the gateway.purchase() method.
        """
        if self.error or self.status in ["N", "U"]:
            # Proceeding with status "U" is allowed, but risky
            return False, {}

        if self.status in ["Y", "A"]:
            mpi_data = {'eci': self.eci,
                        'xid': self.xid,
                        'cavv': self.cavv,
                        }
            return True, {'mpi': mpi_data}

        return False, {}
