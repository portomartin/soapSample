import datetime
import xml.etree.ElementTree as ET

from lxml import etree
from functools import wraps
from lxml.builder import ElementMaker

from .. wsaa import parse_token


class InvalidReceiptNumber(Exception):
    pass


# XML helpers
SOAP_NS = 'http://schemas.xmlsoap.org/soap/envelope/'
SOAP = ElementMaker(namespace=SOAP_NS, nsmap={'soap': SOAP_NS})

FE_NS = 'http://ar.gov.afip.dif.FEV1/'
FE = ElementMaker(namespace=FE_NS, nsmap={None: FE_NS})


def current_datetime(delta_day=0, delta_hour=0, delta_min=0):
    """Returns the current date time (plus adding an optional delta)."""

    dt = datetime.date.today() + datetime.timedelta(days=delta_day,
                                                    hours=delta_hour,
                                                    minutes=delta_min)
    # TODO: appending the milliseconds in the time zone as a workaround. The milliseconds are
    #       included in the real WSAA response, so we must make it as real as we can
    return dt.strftime('%Y-%m-%dT%H:%M:%S.000-03:00')


def soap_fault(code, string):
    """Returns a string representing a SOAP fault response."""

    return """
        <?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <soap:Body>
                <soap:Fault>
                    <faultcode>%(code)s</faultcode>
                    <faultstring>%(string)s</faultstring>
                    <detail />
                </soap:Fault>
            </soap:Body>
        </soap:Envelope>
        """ % locals()


def soap_error_token_expired(handler):
    # gets the action received
    soap_action = handler.headers.get('SOAPAction').split('/')[-1]

    error = etree.Element('%sResponse' % soap_action, nsmap={None: FE_NS})
    tmp = etree.SubElement(error, '%sResult' % soap_action)
    tmp = etree.SubElement(tmp, 'Errors')
    tmp = etree.SubElement(tmp, 'Err')

    # sets the error code and message
    code = etree.SubElement(tmp, 'Code')
    code.text = '600'

    # TODO: use real dates?
    msg = etree.SubElement(tmp, 'Msg')
    msg.text = 'ValidacionDeToken: No validaron las fechas del token ' + \
               'GenTime, ExpTime, NowUTC: 1604411056 (11/3/2020 1:43:46 PM)' + \
               ', 1604454316 (11/4/2020 1:45:16 AM), 11/6/2020 3:58:28 PM'

    send_soap_envelope(handler, error)


def soap_error_action_missing(handler):
    """Sends a SOAP fault because the SOAPAction was not valid."""

    # the testing server returns HTTP error 500 when nos provided with a SOAPAction
    handler.send_response(500)
    handler.end_headers()

    response = soap_fault(code='soap:Client',
                          string='Unable to handle request without a valid action parameter.' + \
                                 'Please supply a valid soap action.')
    handler.wfile.write(response)


def send_soap_envelope(handler, payload):
    """Sends a SOAP response wrapping `payload` (an XML element) in a SOAP envelope."""

    envelope = SOAP.Envelope(
        SOAP.Header(
            FE.FEHeaderInfo(
                FE.ambiente('Mock'),
                FE.fecha(current_datetime()),
                FE.id('4.0.0.0')
            )
        ),
        SOAP.body(payload)
    )

    handler.send_response(200)
    handler.end_headers()
    handler.wfile.write(etree.tostring(envelope, encoding='utf-8', xml_declaration=True))


def ValidateToken(func):
    """Decorator for WSFEv1 SOAP methods that checks the fake WSAA token is valid. If the token is
    expired, the request is rejected wit an error.
    The wrapped function will receive (besides the handler) the client's tributary ID."""

    @wraps(func)
    def _wrapper(handler):
        root = ET.fromstring(handler.body_contents)

        ns = {'ar': 'http://ar.gov.afip.dif.FEV1/'}
        token_elem = root.find('.//ar:Token', ns)

        if token_elem is None or handler.server.is_token_expired(token_elem.text):
            soap_error_token_expired(handler)
            return

        tributary_id = parse_token(token_elem.text)

        # if the token was successfully validated, calls the original function
        func(handler, tributary_id)

    return _wrapper
