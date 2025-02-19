"""
Sample application to illustrate how to get a token from the WSAA and authorize documents against
the WSFEv1. For example, request a CAE for a document, request a CAEA and inform a document
authorized using CAEA.
"""

import re
import elba
import requests
import argparse
import xml.etree.ElementTree as ET

from random import randint
from base64 import b64encode
from datetime import datetime, timedelta
from collections import namedtuple


WSAA_URL, WSFEv1_URL = None, None

Token = namedtuple('Token', 'token, sign, expiration, id')
VatAmount = namedtuple('VatAmount', 'type, net_amount, amount')


CUIT_RE = re.compile(r'SERIALNUMBER=CUIT (\d+)')


WSAA_LOGIN_PAYLOAD_TEMPLATE = """\
<?xml version="1.0" encoding="UTF-8"?>
<loginTicketRequest version="1.0">
    <header> 
        <uniqueId>%(unique_id)d</uniqueId>
        <generationTime>%(generation_time)s</generationTime>
        <expirationTime>%(expiration_time)s</expirationTime>
    </header> 
    <service>wsfe</service> 
</loginTicketRequest>
"""

# template for the loginCMS SOAP method of the WSAA. The TRA (base64 encoded CMS) must be
# inserted in the `in0` field.
WSAA_LOGIN_CMS_SOAP_TEMPLATE = """\
<s11:Envelope xmlns:s11='http://schemas.xmlsoap.org/soap/envelope/'>
    <s11:Body>
        <tns1:loginCms xmlns:tns1='http://wsaa.view.sua.dvadac.desein.afip.gov'>
            <tns1:in0>%(TRA)s</tns1:in0>
        </tns1:loginCms>
    </s11:Body>
</s11:Envelope>
"""


class SOAPFault():
    def __init__(self, code, message):
        self.code, self.message = code, message

    def __str__(self):
        return '%s: %s' % (self.code, self.message)


def current_datetime(fmt='%Y-%m-%dT%H:%M:%S', timezone='Z', offset=None):
    """Returns the current datetime in the specified format.
    If `offset` is not None, it should be a `timedelta` object that will be applied to the current
    datetime.
    """

    offset = offset or timedelta(0)
    return (datetime.today() + offset).strftime(fmt) + timezone


def random_32bit_int():
    return randint(0, (1 << 32) - 1)


def get_login_cms_payload(cert_file, private_key_file, duration=1200):
    """Returns a base64 encoded CMS containing the TRA required to get a token from the WSAA."""

    # local import to avoid indirectly importing demo_config (that defines its own ArgumentParser)
    import crypto

    # builds the template fields
    unique_id = random_32bit_int()
    generation_time = current_datetime(timezone='-03:00')
    expiration_time = current_datetime(timezone='-03:00', offset=timedelta(seconds=duration))

    # generates the payload from the template
    payload = WSAA_LOGIN_PAYLOAD_TEMPLATE % locals()

    cms = crypto.cms_sign(data=payload, signer=cert_file, inkey=private_key_file, outform='der')
    return b64encode(cms)


def parse_fault(xml_string):
    """Parses fault from a SOAP response and returns the error code and message as a tuple."""

    root = ET.fromstring(xml_string)

    ns = {'soapenv': "http://schemas.xmlsoap.org/soap/envelope/"}
    code = root.find('.//faultcode').text
    message = root.find('.//faultstring').text

    return code, message


def get_token(cert_file, private_key_file, duration=1200):
    """Requests a token from the WSAA server for the given `cert_file` and `private_key_file`.
    `cert_file` must be the path to the file containing the certificate that signs the request
    using the private key stored in `private_key_file`.
    The signed request will be valid from the current date until the number of seconds `duration`
    elapses.
    The returned token must be used to communicate with the other web services."""

    TRA = get_login_cms_payload(cert_file, private_key_file, duration)

    response = requests.post('%s/ws/services/LoginCms' % WSAA_URL,
                             data=WSAA_LOGIN_CMS_SOAP_TEMPLATE % locals(),
                             headers={
                                'SOAPAction': '',
                                'Content-Type': 'text/xml',
                            })

    if not response.ok:
        code, message = parse_fault(response.text)
        raise SOAPFault(code, message)

    return extract_token_from_response(wsaa_response=response.text)


def extract_token_from_response(wsaa_response):
    """Extracts the auth token from the response obtained from the WSAA. `wsaa_response` must be
    the body of the response as a string.
    Returns a tuple (token, sign)"""

    root = ET.fromstring(wsaa_response)

    ns = {'afip': "http://wsaa.view.sua.dvadac.desein.afip.gov"}
    response_body = root.find('.//afip:loginCmsReturn', ns).text

    # the response body is an XML text (WTF?), so it needs to be parsed to extract the token
    body = ET.fromstring(response_body)
    id = CUIT_RE.match(body.find('.//destination').text).group(1)
    return Token(body.find('.//token').text, body.find('.//sign').text, body.find('.//expirationTime').text, id)


def build_auth_header(token):
    """Returns the XML defining the authentication header.
    `token` must be a valid Token instance obtained from the WSAA."""

    return """
    <ar:Auth>
        <ar:Token>%(token)s</ar:Token>
        <ar:Sign>%(sign)s</ar:Sign>
        <ar:Cuit>%(id)s</ar:Cuit>
    </ar:Auth>""" % token._asdict()


def build_vats(vats):
    """Returns the XML defining the array of VATs in the receipt.
    `vats` must be an iterable where each element is of type `VatAmount` that contains the
    VAT type, tax base (base imponible) and vat amount."""

    def serialize_vat(vat):
        return '<ar:AlicIva>' \
                    '<ar:Id>%(type)d</ar:Id>' \
                    '<ar:BaseImp>%(net_amount)s</ar:BaseImp>' \
                    '<ar:Importe>%(amount)s</ar:Importe>' \
                '</ar:AlicIva>' % vat._asdict()

    return '<ar:Iva>%s</ar:Iva>' % '\n'.join(map(serialize_vat, vats))


def build_receipt_data(doc_num, doc_type, cuit=None, pos=None, assoc_doc_num=None, assoc_doc_date=None):
    """Returns the XML defining the receipt data."""

    receipt_a_codes = [1, 3]
    receipt_c_codes = [11, 13]
    credit_note_codes = {
      3: 1,
      8: 6,
      13: 11,
    }

    concept = 1 # products
    doc_date = datetime.now().strftime('%Y%m%d')
    currency_id, currency_price = 'PES', '1.000000'
    # id_type, id_num = 96, 35317279  # type of buyer's tributary ID and the ID itself
    id_type, id_num = 99, 0  # type of buyer's tributary ID and the ID itself

    if doc_type in receipt_c_codes:
      gross_total, untaxed_net_total, net_total, untaxed_total = '90.50', '0.00', '90.50', '0.00'
      vat_total, tributes_total = '0.00', '0.00'
      vats = ''  # type -> FEParamGetTiposIva
    else:
      if doc_type in receipt_a_codes:
        id_type, id_num = 80, 30584620389  # type of buyer's tributary ID and the ID itself
      gross_total, untaxed_net_total, net_total, untaxed_total = '104.00', '1.00', '90.50', '3.00'
      vat_total, tributes_total = '9.51', '0.00'
      vats = build_vats([VatAmount(type=4, net_amount='90.50', amount='9.51')])  # type -> FEParamGetTiposIva

    associated_docs = ''
    if doc_type in credit_note_codes.keys():
      assoc_doc_type = credit_note_codes[doc_type]
      associated_docs = """
        <ar:CbtesAsoc>
          <ar:CbteAsoc>
            <ar:Tipo>%(assoc_doc_type)d</ar:Tipo>
            <ar:PtoVta>%(pos)d</ar:PtoVta>
            <ar:Nro>%(doc_num)d</ar:Nro>
            <ar:Cuit>%(cuit)s</ar:Cuit>
            <ar:CbteFch>%(assoc_doc_date)s</ar:CbteFch>
          </ar:CbteAsoc>
        </ar:CbtesAsoc>
          """ % locals()

    return """
        <ar:Concepto>%(concept)d</ar:Concepto>
        <ar:DocTipo>%(id_type)d</ar:DocTipo>
        <ar:DocNro>%(id_num)d</ar:DocNro>
        <ar:CbteDesde>%(doc_num)d</ar:CbteDesde>
        <ar:CbteHasta>%(doc_num)d</ar:CbteHasta>
        <ar:CbteFch>%(doc_date)s</ar:CbteFch>
        <ar:ImpTotal>%(gross_total)s</ar:ImpTotal>
        <ar:ImpTotConc>%(untaxed_net_total)s</ar:ImpTotConc>
        <ar:ImpNeto>%(net_total)s</ar:ImpNeto>
        <ar:ImpOpEx>%(untaxed_total)s</ar:ImpOpEx>
        <ar:ImpTrib>%(tributes_total)s</ar:ImpTrib>
        <ar:ImpIVA>%(vat_total)s</ar:ImpIVA>
        <ar:MonId>%(currency_id)s</ar:MonId>
        <ar:MonCotiz>%(currency_price)s</ar:MonCotiz>
        %(vats)s
        %(associated_docs)s""" % locals()


def build_caea_request(token, period, fortnight):
    """Returns the XML payload for the CAEA request.
    `token` must be a valid Token instance obtained from the WSAA."""

    auth = build_auth_header(token)

    return """<?xml version="1.0"?>
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ar="http://ar.gov.afip.dif.FEV1/">
      <soapenv:Header/>
      <soapenv:Body>
        <ar:FECAEASolicitar>
          %(auth)s
          <ar:Periodo>%(period)s</ar:Periodo>
          <ar:Orden>%(fortnight)d</ar:Orden>
        </ar:FECAEASolicitar>
      </soapenv:Body>
    </soapenv:Envelope>
    """ % locals()


def build_inform_caea_request(token, caea, pos, doc_type, doc_num, contingency=False):
    """Returns the XML payload for the information of a document authorized using CAEA.
    `token` must be a valid Token instance obtained from the WSAA."""

    auth = build_auth_header(token)
    num_records = 1
    receipt_data = build_receipt_data(doc_num=doc_num, doc_type=doc_type)
    contingency_datetime = '<ar:CbteFchHsGen>%s</ar:CbteFchHsGen>' % datetime.now().strftime('%Y%m%d%H%M%S') if contingency is True else ''

    return """<?xml version="1.0"?>
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ar="http://ar.gov.afip.dif.FEV1/">
      <soapenv:Header/>
      <soapenv:Body>
        <ar:FECAEARegInformativo>
          %(auth)s
          <ar:FeCAEARegInfReq>
            <ar:FeCabReq>
              <ar:CantReg>%(num_records)d</ar:CantReg>
              <ar:PtoVta>%(pos)d</ar:PtoVta>
              <ar:CbteTipo>%(doc_type)d</ar:CbteTipo>
            </ar:FeCabReq>
            <ar:FeDetReq>
              <ar:FECAEADetRequest>
                %(receipt_data)s
                <ar:CAEA>%(caea)s</ar:CAEA>
                '<ar:CbteFchHsGen>%(contingency_datetime)s</ar:CbteFchHsGen>'
              </ar:FECAEADetRequest>
            </ar:FeDetReq>
          </ar:FeCAEARegInfReq>
        </ar:FECAEARegInformativo>
      </soapenv:Body>
    </soapenv:Envelope>
    """ % locals()


def build_caea_data_request(token, period, fortnight):
    """Returns the XML payload for the CAEA data request.
    `token` must be a valid Token instance obtained from the WSAA."""

    auth = build_auth_header(token)

    return """<?xml version="1.0"?>
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ar="http://ar.gov.afip.dif.FEV1/">
      <soapenv:Header/>
      <soapenv:Body>
        <ar:FECAEAConsultar>
          %(auth)s
          <ar:Periodo>%(period)s</ar:Periodo>
          <ar:Orden>%(fortnight)d</ar:Orden>
        </ar:FECAEAConsultar>
      </soapenv:Body>
    </soapenv:Envelope>
    """ % locals()


def build_inform_caea_no_movement_request(token, caea, pos):
    """Returns the XML payload for the information of a CAEA with no movement request.
    `token` must be a valid Token instance obtained from the WSAA."""

    auth = build_auth_header(token)

    return """<?xml version="1.0"?>
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ar="http://ar.gov.afip.dif.FEV1/">
      <soapenv:Header/>
      <soapenv:Body>
        <ar:FECAEASinMovimientoInformar>
          %(auth)s
          <ar:PtoVta>%(pos)d</ar:PtoVta>
          <ar:CAEA>%(caea)s</ar:CAEA>
        </ar:FECAEASinMovimientoInformar>
      </soapenv:Body>
    </soapenv:Envelope>
    """ % locals()


def build_get_caea_no_movement_request(token, caea, pos):
    """Returns the XML payload for the CAEA with no movement request.
    `token` must be a valid Token instance obtained from the WSAA."""

    auth = build_auth_header(token)

    return """<?xml version="1.0"?>
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ar="http://ar.gov.afip.dif.FEV1/">
      <soapenv:Header/>
      <soapenv:Body>
        <ar:FECAEASinMovimientoConsultar>
          %(auth)s
          <ar:CAEA>%(caea)s</ar:CAEA>
          <ar:PtoVta>%(pos)d</ar:PtoVta>
        </ar:FECAEASinMovimientoConsultar>
      </soapenv:Body>
    </soapenv:Envelope>
    """ % locals()


def build_cae_request(token, pos, doc_type, doc_num, assoc_doc_num=None, assoc_doc_date=None):
    """Returns the XML payload for the CAE request.
    `token` must be a valid Token instance obtained from the WSAA.
    `doc_num` is the number of the document to authorize.
    `assoc_doc_num` is the number of the associated document (in case of debit or credit notes).
    `assoc_doc_date` is the date of the associated document.
    """

    auth = build_auth_header(token)
    num_records = 1
    receipt_data = build_receipt_data(doc_num=doc_num, doc_type=doc_type, cuit=token._asdict()['id'], pos=pos, assoc_doc_num=assoc_doc_num, assoc_doc_date=assoc_doc_date)

    return """<?xml version="1.0"?>
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ar="http://ar.gov.afip.dif.FEV1/">
      <soapenv:Header/>
      <soapenv:Body>
        <ar:FECAESolicitar>
          %(auth)s
          <ar:FeCAEReq>
            <ar:FeCabReq>
              <ar:CantReg>%(num_records)d</ar:CantReg>
              <ar:PtoVta>%(pos)d</ar:PtoVta>
              <ar:CbteTipo>%(doc_type)d</ar:CbteTipo>
            </ar:FeCabReq>
            <ar:FeDetReq>
              <ar:FECAEDetRequest>
                %(receipt_data)s
              </ar:FECAEDetRequest>
            </ar:FeDetReq>
          </ar:FeCAEReq>
        </ar:FECAESolicitar>
      </soapenv:Body>
    </soapenv:Envelope>
    """ % locals()


def build_last_auth_doc_request(token, pos, doc_type):
    """Returns the XML payload for the last authorized document number request.
    `token` must be a valid Token instance obtained from the WSAA."""

    auth = build_auth_header(token)
    return """<?xml version="1.0"?>
        <soap-env:Envelope xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/">
          <soap-env:Body>
            <ar:FECompUltimoAutorizado xmlns:ar="http://ar.gov.afip.dif.FEV1/">
              %(auth)s
              <ar:PtoVta>%(pos)s</ar:PtoVta>
              <ar:CbteTipo>%(doc_type)s</ar:CbteTipo>
            </ar:FECompUltimoAutorizado>
          </soap-env:Body>
        </soap-env:Envelope>""" % locals()


def build_auth_doc_data_request(token, pos, doc_type, doc_num):
    """Returns the XML payload for the request of the data of an authorized receipt.
    `token` must be a valid Token instance obtained from the WSAA."""

    auth = build_auth_header(token)
    return """<?xml version="1.0"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ar="http://ar.gov.afip.dif.FEV1/">
          <soapenv:Header/>
          <soapenv:Body>
            <ar:FECompConsultar>
              %(auth)s
              <ar:FeCompConsReq>
                <ar:CbteTipo>%(doc_type)s</ar:CbteTipo>
                <ar:CbteNro>%(doc_num)s</ar:CbteNro>
                <ar:PtoVta>%(pos)s</ar:PtoVta>
              </ar:FeCompConsReq>
            </ar:FECompConsultar>
          </soapenv:Body>
        </soapenv:Envelope>""" % locals()


def build_get_optionals_request(token):
    """Returns the XML payload for the optionals request.
    `token` must be a valid Token instance obtained from the WSAA."""

    auth = build_auth_header(token)
    return """<?xml version="1.0"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ar="http://ar.gov.afip.dif.FEV1/">
          <soapenv:Header/>
          <soapenv:Body>
            <ar:FEParamGetTiposOpcional>
              %(auth)s
            </ar:FEParamGetTiposOpcional>
          </soapenv:Body>
        </soapenv:Envelope>""" % locals()


def build_get_other_tributes_request(token):
    """Returns the XML payload for the other tributes request.
    `token` must be a valid Token instance obtained from the WSAA."""

    auth = build_auth_header(token)
    return """<?xml version="1.0"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ar="http://ar.gov.afip.dif.FEV1/">
          <soapenv:Header/>
          <soapenv:Body>
            <ar:FEParamGetTiposTributos>
              %(auth)s
            </ar:FEParamGetTiposTributos>
          </soapenv:Body>
        </soapenv:Envelope>""" % locals()


def build_get_vats_request(token):
    """Returns the XML payload for the vats request.
    `token` must be a valid Token instance obtained from the WSAA."""

    auth = build_auth_header(token)
    return """<?xml version="1.0"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ar="http://ar.gov.afip.dif.FEV1/">
          <soapenv:Header/>
          <soapenv:Body>
            <ar:FEParamGetTiposIva>
              %(auth)s
            </ar:FEParamGetTiposIva>
          </soapenv:Body>
        </soapenv:Envelope>""" % locals()


def build_get_pos_numbers_request(token):
    """Returns the XML payload for the user's POS numbers request.
    `token` must be a valid Token instance obtained from the WSAA."""

    auth = build_auth_header(token)
    return """<?xml version="1.0"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ar="http://ar.gov.afip.dif.FEV1/">
          <soapenv:Header/>
          <soapenv:Body>
            <ar:FEParamGetPtosVenta>
              %(auth)s
            </ar:FEParamGetPtosVenta>
          </soapenv:Body>
        </soapenv:Envelope>""" % locals()


def request_caea(token, period, fortnight):
    """Sends a request to the WSFE to obtain a CAEA for the given period. Returns the authorized CAEA.
    `token` must be a Token instance with the fields obtained from the WSAA (not expired)."""

    req = build_caea_request(token, period=period, fortnight=fortnight)

    # executes the SOAP method
    response = requests.post('%s/wsfev1/service.asmx' % WSFEv1_URL,
                             data=req,
                             headers={
                                'SOAPAction': 'http://ar.gov.afip.dif.FEV1/FECAEASolicitar',
                                'Content-Type': 'text/xml',
                            })

    if not response.ok:
        code, message = parse_fault(response.text)
        raise SOAPFault(code, message)

    return response.text


def inform_caea_document(token, caea, pos, doc_type, doc_num, contingency=False):
    """Sends a request to the WSFE to inform a document authorized with the given CAEA. Returns the
    authorized receipt data.
    `token` must be a Token instance with the fields obtained from the WSAA (not expired)."""

    req = build_inform_caea_request(token, caea=caea, pos=pos, doc_type=doc_type, doc_num=doc_num, contingency=contingency)

    # executes the SOAP method
    response = requests.post('%s/wsfev1/service.asmx' % WSFEv1_URL,
                             data=req,
                             headers={
                                'SOAPAction': 'http://ar.gov.afip.dif.FEV1/FECAEARegInformativo',
                                'Content-Type': 'text/xml',
                            })

    if not response.ok:
        code, message = parse_fault(response.text)
        raise SOAPFault(code, message)

    return response.text


def request_caea_data(token, period, fortnight):
    """Sends a request to the WSFE to obtain the information about a previously authorized CAEA for
    the given period. Returns the authorized CAEA information.
    `token` must be a Token instance with the fields obtained from the WSAA (not expired)."""

    req = build_caea_data_request(token, period=period, fortnight=fortnight)

    # executes the SOAP method
    response = requests.post('%s/wsfev1/service.asmx' % WSFEv1_URL,
                             data=req,
                             headers={
                                'SOAPAction': 'http://ar.gov.afip.dif.FEV1/FECAEAConsultar',
                                'Content-Type': 'text/xml',
                            })

    if not response.ok:
        code, message = parse_fault(response.text)
        raise SOAPFault(code, message)

    return response.text


def inform_caea_no_movement(token, caea, pos):
    """Sends a request to the WSFE to register a CAEA with no movement for a POS.
    `token` must be a Token instance with the fields obtained from the WSAA (not expired)."""

    req = build_inform_caea_no_movement_request(token, caea=caea, pos=pos)

    # executes the SOAP method
    response = requests.post('%s/wsfev1/service.asmx' % WSFEv1_URL,
                             data=req,
                             headers={
                                'SOAPAction': 'http://ar.gov.afip.dif.FEV1/FECAEASinMovimientoInformar',
                                'Content-Type': 'text/xml',
                            })

    if not response.ok:
        code, message = parse_fault(response.text)
        raise SOAPFault(code, message)

    return response.text


def request_caea_no_movement(token, caea, pos):
    """Sends a request to the WSFE to obtain the CAEAs registered with no movement for a POS.
    `token` must be a Token instance with the fields obtained from the WSAA (not expired)."""

    req = build_get_caea_no_movement_request(token, caea=caea, pos=pos)

    # executes the SOAP method
    response = requests.post('%s/wsfev1/service.asmx' % WSFEv1_URL,
                             data=req,
                             headers={
                                'SOAPAction': 'http://ar.gov.afip.dif.FEV1/FECAEASinMovimientoConsultar',
                                'Content-Type': 'text/xml',
                            })

    if not response.ok:
        code, message = parse_fault(response.text)
        raise SOAPFault(code, message)

    return response.text


def request_cae(token, pos, doc_type, doc_num, assoc_doc_num=None, assoc_doc_date=None):
    """Sends a request to the WSFE to obtain the CAE for a particular document. Returns the CAE and
    authorization date.
    `token` must be a Token instance with the fields obtained from the WSAA (not expired)."""

    req = build_cae_request(token, pos=pos, doc_type=doc_type, doc_num=doc_num, assoc_doc_num=assoc_doc_num, assoc_doc_date=assoc_doc_date)

    # executes the SOAP method
    response = requests.post('%s/wsfev1/service.asmx' % WSFEv1_URL,
                             data=req,
                             headers={
                                'SOAPAction': 'http://ar.gov.afip.dif.FEV1/FECAESolicitar',
                                'Content-Type': 'text/xml',
                            })

    if not response.ok:
        code, message = parse_fault(response.text)
        raise SOAPFault(code, message)

    return response.text


def request_last_auth_doc(token, pos, doc_type):
    """Executes the FECompUltimoAutorizado method."""

    req = build_last_auth_doc_request(token, pos=pos, doc_type=doc_type)

    # executes the SOAP method
    response = requests.post('%s/wsfev1/service.asmx' % WSFEv1_URL,
                             data=req,
                             headers={
                                'SOAPAction': 'http://ar.gov.afip.dif.FEV1/FECompUltimoAutorizado',
                                'Content-Type': 'text/xml',
                            })

    if not response.ok:
        code, message = parse_fault(response.text)
        raise SOAPFault(code, message)

    return response.text


def request_auth_doc_data(token, pos, doc_type, doc_num):
    """Executes the FECompConsultar method."""

    req = build_auth_doc_data_request(token, pos=pos, doc_type=doc_type, doc_num=doc_num)

    # executes the SOAP method
    response = requests.post('%s/wsfev1/service.asmx' % WSFEv1_URL,
                             data=req,
                             headers={
                                'SOAPAction': 'http://ar.gov.afip.dif.FEV1/FECompConsultar',
                                'Content-Type': 'text/xml',
                            })

    if not response.ok:
        code, message = parse_fault(response.text)
        raise SOAPFault(code, message)

    return response.text


def get_optionals(token):
    """Executes the FEParamGetTiposOpcional method."""

    req = build_get_optionals_request(token)

    # executes the SOAP method
    response = requests.post('%s/wsfev1/service.asmx' % WSFEv1_URL,
                             data=req,
                             headers={
                                'SOAPAction': 'http://ar.gov.afip.dif.FEV1/FEParamGetTiposOpcional',
                                'Content-Type': 'text/xml',
                            })

    if not response.ok:
        code, message = parse_fault(response.text)
        raise SOAPFault(code, message)

    return response.text


def get_other_tributes(token):
    """Executes the FEParamGetTiposTributos method."""

    req = build_get_other_tributes_request(token)

    # executes the SOAP method
    response = requests.post('%s/wsfev1/service.asmx' % WSFEv1_URL,
                             data=req,
                             headers={
                                'SOAPAction': 'http://ar.gov.afip.dif.FEV1/FEParamGetTiposTributos',
                                'Content-Type': 'text/xml',
                            })

    if not response.ok:
        code, message = parse_fault(response.text)
        raise SOAPFault(code, message)

    return response.text


def get_vats(token):
    """Executes the FEParamGetTiposIva method."""

    req = build_get_vats_request(token)

    # executes the SOAP method
    response = requests.post('%s/wsfev1/service.asmx' % WSFEv1_URL,
                             data=req,
                             headers={
                                'SOAPAction': 'http://ar.gov.afip.dif.FEV1/FEParamGetTiposIva',
                                'Content-Type': 'text/xml',
                            })

    if not response.ok:
        code, message = parse_fault(response.text)
        raise SOAPFault(code, message)

    return response.text


def get_pos_numbers(token):
    """Executes the FEParamGetPtosVenta method."""

    req = build_get_pos_numbers_request(token)

    # executes the SOAP method
    response = requests.post('%s/wsfev1/service.asmx' % WSFEv1_URL,
                             data=req,
                             headers={
                                'SOAPAction': 'http://ar.gov.afip.dif.FEV1/FEParamGetPtosVenta',
                                'Content-Type': 'text/xml',
                            })

    if not response.ok:
        code, message = parse_fault(response.text)
        raise SOAPFault(code, message)

    return response.text


def request_receipt_types(token):
    """Executes the FEParamGetTiposCbte method."""

    auth = build_auth_header(token)
    req = """<?xml version="1.0"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ar="http://ar.gov.afip.dif.FEV1/">
          <soapenv:Header/>
          <soapenv:Body>
            <ar:FEParamGetTiposCbte>
              %(auth)s
            </ar:FEParamGetTiposCbte>
          </soapenv:Body>
        </soapenv:Envelope>""" % locals()

    # executes the SOAP method
    response = requests.post('%s/wsfev1/service.asmx' % WSFEv1_URL,
                             data=req,
                             headers={
                                'SOAPAction': 'http://ar.gov.afip.dif.FEV1/FEParamGetTiposCbte',
                                'Content-Type': 'text/xml',
                            })

    if not response.ok:
        code, message = parse_fault(response.text)
        raise SOAPFault(code, message)

    return response.text


def dummy():
    """Executes the FEDummy method."""

    req = """<?xml version="1.0"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ar="http://ar.gov.afip.dif.FEV1/">
          <soapenv:Header/>
          <soapenv:Body>
            <ar:FEDummy/>
          </soapenv:Body>
        </soapenv:Envelope>""" % locals()

    # executes the SOAP method
    response = requests.post('%s/wsfev1/service.asmx' % WSFEv1_URL,
                             data=req,
                             headers={
                                'SOAPAction': 'http://ar.gov.afip.dif.FEV1/FEDummy',
                                'Content-Type': 'text/xml',
                            })

    if not response.ok:
        code, message = parse_fault(response.text)
        raise SOAPFault(code, message)

    return response.text


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument("--wsaa_host", metavar='URL', default='https://wsaahomo.afip.gov.ar', help="WSAA's Host URL (without the path). Defaults to the homologation service URL.")
    parser.add_argument("--wsfe_host", metavar='URL', default='https://wswhomo.afip.gov.ar', help="WSFEv1's Host URL (without the path). Defaults to the homologation service URL.")
    parser.add_argument("cert", help="Certificate authorized for WSAA (PEM).")
    parser.add_argument("private_key", help="Private key that corresponds the certificate (PEM).")

    args = parser.parse_args()

    WSAA_URL, WSFEv1_URL = args.wsaa_host, args.wsfe_host

    token = Token(token='PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9InllcyI/Pgo8c3NvIHZlcnNpb249IjIuMCI+CiAgICA8aWQgc3JjPSJDTj13c2FhaG9tbywgTz1BRklQLCBDPUFSLCBTRVJJQUxOVU1CRVI9Q1VJVCAzMzY5MzQ1MDIzOSIgZHN0PSJDTj13c2ZlLCBPPUFGSVAsIEM9QVIiIHVuaXF1ZV9pZD0iMTc3MzE0NDAwNSIgZ2VuX3RpbWU9IjE2Mjk3NTg0NDAiIGV4cF90aW1lPSIxNjI5ODAxNzAwIi8+CiAgICA8b3BlcmF0aW9uIHR5cGU9ImxvZ2luIiB2YWx1ZT0iZ3JhbnRlZCI+CiAgICAgICAgPGxvZ2luIGVudGl0eT0iMzM2OTM0NTAyMzkiIHNlcnZpY2U9IndzZmUiIHVpZD0iU0VSSUFMTlVNQkVSPUNVSVQgMjAzODE1MTAxMTYsIENOPWVpbnZvaWNlIiBhdXRobWV0aG9kPSJjbXMiIHJlZ21ldGhvZD0iMjIiPgogICAgICAgICAgICA8cmVsYXRpb25zPgogICAgICAgICAgICAgICAgPHJlbGF0aW9uIGtleT0iMjAzODE1MTAxMTYiIHJlbHR5cGU9IjQiLz4KICAgICAgICAgICAgPC9yZWxhdGlvbnM+CiAgICAgICAgPC9sb2dpbj4KICAgIDwvb3BlcmF0aW9uPgo8L3Nzbz4K', sign='e/IY9jeJfPqzTnbDHUdw5Xa3nKbfVKsrblP4/nYNDLZCRdZJ/hZRH3F/Bmfmq8wE1RV5ZD3c4fViwYWylTUum3G6Q08cZdr3+HCsb6xte2/8edLKTJ7C8Sm0ZltuIKaHNuPK+4oMmI1gAQFxPFCltKf9YaJ1GBYJ6MzpnZJodJg=', expiration='2021-08-24T07:41:40.952-03:00', id='20381510116')
    token = get_token(args.cert, args.private_key, duration=30)
    # always print the token because we need to reuse it due to AFIP's server cooldown
    print token
    
    # CAE related methods
    # 
    # Requests a CAE
    # request_cae(token=token, pos=<POS number>, doc_type=<Factura A, B, etc>, doc_num=<Document number>, assoc_doc_num=<Associated document number>, assoc_doc_date=<Assoc. doc. date>)
    # examples:
    print request_cae(token=token, pos=1, doc_type=6, doc_num=1)
    # print request_cae(token=token, pos=1, doc_type=3, doc_num=5, assoc_doc_num=1, assoc_doc_date='20210222')
    # 
    # Request the last authorized document (both CAE and CAEA) for a given POS and receipt type
    # examples:
    print request_last_auth_doc(token=token, pos=1, doc_type=6)
    # print request_last_auth_doc(token=token, pos=9901, doc_type=1)
    # 
    # Request the data of an authorized document (both CAE and CAEA) for a given POS and receipt type
    # examples:
    print request_auth_doc_data(token=token, pos=1, doc_type=6, doc_num=1)
    # print request_auth_doc_data(token=token, pos=9902, doc_type=1, doc_num=11)

    # CAEA related methods
    # 
    # Requests a CAEA for a period and fortnight
    # request_caea(token=token, period=<YYYYMM>, fortnight=<1 or 2>)
    # example:
    # print request_caea(token=token, period='202108', fortnight=2)
    # 
    # Request the data of an already granted CAEA
    # request_caea_data(token=token, period='202102', fortnight=2)
    # example:
    # print request_caea_data(token=token, period=<YYYYMM>, fortnight=<1 or 2>)
    # 
    # Informs a document authorized using a CAEA
    # inform_caea_document(token=token, caea=<CAEA>, pos=<POS number>, doc_type=<Factura A, B, etc>, doc_num=<Document number>, contingency=<True or False>)
    # examples:
    # print inform_caea_document(token=token, caea='31346910465562', pos=9901, doc_type=1, doc_num=4, contingency=True)
    # print inform_caea_document(token=token, caea='31346910465562', pos=9902, doc_type=6, doc_num=11, contingency=True)
    # 
    # CAEA with no movement: these methods doesn't seem to work in the homologation server, the CAEA with no movement information
    # is always accepted, and the request of a CAEA with no movement always fails with the error:
    # "El CAEA informado no se encuentra registrado en las bases de la Administracion como sin movimientos."
    # 
    # examples:
    # print inform_caea_no_movement(token=token, caea='31086749381881', pos=9901)
    # print request_caea_no_movement(token=token, caea='31086749381881', pos=9901)

    # AFIP constants
    # 
    # print get_optionals(token)
    # print get_other_tributes(token)
    # print get_vats(token)
    # print get_pos_numbers(token)
    # print request_receipt_types(token=token)
    
    # AFIP server status
    # print dummy()

